import json
import re
import traceback
from datetime import datetime

import streamlit as st
from groq import Groq

# ==================== HELPERS ====================


def validate_and_fix_belief(belief: dict, user_input: str) -> dict:
    """Post-processing validation untuk memperbaiki angka & field yang salah dari LLM."""
    input_lower = user_input.lower()

    # Fix days_since_purchase
    days_patterns = [
        (r"(\d+)\s*hari(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1))),
        (r"(\d+)\s*minggu(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1)) * 7),
        (r"(\d+)\s*bulan(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1)) * 30),
        (r"kemarin", lambda m: 1),
        (r"baru\s*beli", lambda m: 1),
    ]
    for pattern, extractor in days_patterns:
        match = re.search(pattern, input_lower)
        if match:
            belief["days_since_purchase"] = extractor(match)
            break

    # Fix estimated_value
    value_patterns = [
        (r"(?:rp\.?\s*)?(\d+)\s*(?:jt|juta)", lambda m: int(m.group(1)) * 1_000_000),
        (r"(?:rp\.?\s*)?(\d+)\s*(?:rb|ribu)", lambda m: int(m.group(1)) * 1_000),
        (r"(?:rp\.?\s*)?(\d{1,3}(?:[.,]\d{3})+)", lambda m: int(re.sub(r"[.,]", "", m.group(1)))),
    ]
    for pattern, extractor in value_patterns:
        match = re.search(pattern, input_lower)
        if match:
            belief["estimated_value"] = extractor(match)
            break

    # Fix has_proof
    proof_keywords = ["foto", "gambar", "bukti", "photo", "picture", "screenshot", "ss"]
    if any(word in input_lower for word in proof_keywords):
        belief["has_proof"] = True

    # Fix emotion_score
    high_emotion_words = [
        "gila",
        "kacau",
        "parah",
        "marah",
        "jelek banget",
        "kesal",
        "sebel",
        "ngamuk",
        "frustrasi",
        "kecewa banget",
    ]
    if any(word in input_lower for word in high_emotion_words):
        belief["emotion_score"] = max(belief.get("emotion_score", 5), 8)

    # Pastikan tipe data benar
    belief["days_since_purchase"] = int(belief.get("days_since_purchase", 0) or 0)
    belief["estimated_value"] = int(belief.get("estimated_value", 0) or 0)
    belief["emotion_score"] = int(belief.get("emotion_score", 5) or 5)
    belief["has_proof"] = bool(belief.get("has_proof", False))

    return belief


def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        import os

        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY tidak ditemukan di secrets atau environment variable")
    return Groq(api_key=api_key)


def safe_json(data):
    """Helper biar st.json tidak error."""
    try:
        return data
    except Exception:
        return {"error": "Gagal render JSON", "raw": str(data)}


# ==================== AGENT ====================


class LayanAgent:
    def __init__(self):
        self.audit_log = []
        self.rules = {
            "max_auto_refund_days": 14,
            "max_auto_refund_amount": 5_000_000,
            "requires_proof_for_damage": True,
        }
        self.last_error = None

    def _log(self, stage: str, details: dict):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage,
            "details": details,
        }
        self.audit_log.append(entry)

    def _llm_extract_belief(self, user_input: str) -> dict:
        self._log("LLM_PERCEPTION", {"raw_input": user_input})

        system_prompt = """
You are an expert Customer Service Intent Parser for Indonesian e-commerce.
Extract information EXACTLY from the user message. Do not invent numbers.

Respond ONLY with a valid JSON object (no markdown) matching this schema:
{
  "intent": "request_return_defective" | "general_inquiry" | "other",
  "emotion_score": 1-10,
  "days_since_purchase": integer,
  "has_proof": boolean,
  "estimated_value": integer
}

Rules:
- days_since_purchase: convert "minggu" → *7, "bulan" → *30. Jika tidak disebutkan isi 0.
- estimated_value: convert "juta/jt" → *1000000, "ribu/rb" → *1000. Jika tidak disebutkan isi 0.
- has_proof: true hanya jika user menyebut foto/gambar/bukti/screenshot.
- emotion_score: 8-10 jika ada kata marah/kesal/kacau/parah/gila.
- intent: "request_return_defective" jika ada kata rusak/retak/pecah/cacat.
"""

        try:
            client = get_groq_client()
            completion = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )

            raw_content = completion.choices[0].message.content
            self._log("LLM_RAW_OUTPUT", {"raw_content": raw_content})

            if not raw_content or not raw_content.strip():
                raise ValueError("LLM mengembalikan response kosong")

            # Bersihkan markdown jika ada
            cleaned = raw_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            belief = json.loads(cleaned)
            belief = validate_and_fix_belief(belief, user_input)

            self._log("BELIEF_STATE_CREATED", {"belief": belief, "raw_llm_output": raw_content})
            return belief

        except Exception as e:
            error_detail = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "raw_content": locals().get("raw_content", None),
            }
            self.last_error = error_detail
            self._log("LLM_FALLBACK_TRIGGERED", error_detail)
            return self._fallback_rule_based_parser(user_input)

    def _fallback_rule_based_parser(self, user_input: str) -> dict:
        input_lower = user_input.lower()
        days = 0
        value = 0
        emotion = 5
        has_proof = False

        for pattern, extractor in [
            (r"(\d+)\s*hari(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1))),
            (r"(\d+)\s*minggu(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1)) * 7),
            (r"(\d+)\s*bulan(?:\s*(?:yang\s*)?lalu)?", lambda m: int(m.group(1)) * 30),
            (r"kemarin", lambda m: 1),
        ]:
            match = re.search(pattern, input_lower)
            if match:
                days = extractor(match)
                break

        for pattern, extractor in [
            (r"(?:rp\.?\s*)?(\d+)\s*(?:jt|juta)", lambda m: int(m.group(1)) * 1_000_000),
            (r"(?:rp\.?\s*)?(\d+)\s*(?:rb|ribu)", lambda m: int(m.group(1)) * 1_000),
        ]:
            match = re.search(pattern, input_lower)
            if match:
                value = extractor(match)
                break

        if any(w in input_lower for w in ["gila", "kacau", "parah", "marah", "kesal", "ngamuk"]):
            emotion = 8

        if any(w in input_lower for w in ["foto", "gambar", "bukti", "photo", "screenshot"]):
            has_proof = True

        if any(w in input_lower for w in ["retak", "rusak", "pecah", "defect", "cacat"]):
            belief = {
                "intent": "request_return_defective",
                "emotion_score": emotion,
                "days_since_purchase": days,
                "has_proof": has_proof,
                "estimated_value": value,
            }
        else:
            belief = {
                "intent": "general_inquiry",
                "emotion_score": 3,
                "days_since_purchase": 0,
                "has_proof": False,
                "estimated_value": 0,
            }

        self._log("FALLBACK_PARSER_RESULT", belief)
        return belief

    def _bdi_evaluate_intention(self, belief: dict) -> dict:
        self._log("BDI_RULE_EVALUATION_START", {"checking_rules_against": belief})
        decision = {"action": "unknown", "reason": "", "escalate_to_human": False}

        if belief.get("intent") == "request_return_defective":
            if belief["estimated_value"] > self.rules["max_auto_refund_amount"]:
                decision["action"] = "escalate_to_human"
                decision["escalate_to_human"] = True
                decision["reason"] = (
                    f"Nilai estimasi ({belief['estimated_value']:,}) melebihi batas "
                    f"otorisasi bot ({self.rules['max_auto_refund_amount']:,}). "
                    f"Perlu verifikasi manusia."
                )
            elif belief["days_since_purchase"] > self.rules["max_auto_refund_days"]:
                decision["action"] = "reject_out_of_warranty"
                decision["reason"] = f"Melebihi batas {self.rules['max_auto_refund_days']} hari."
            elif self.rules["requires_proof_for_damage"] and not belief["has_proof"]:
                decision["action"] = "request_proof"
                decision["reason"] = (
                    "Bukti kerusakan (foto) wajib dilampirkan sebelum proses refund."
                )
            else:
                decision["action"] = "approve_auto_refund"
                decision["reason"] = "Semua syarat terpenuhi."
        else:
            decision["action"] = "general_response"
            decision["reason"] = "Intent tidak memerlukan validasi retur."

        self._log("INTENTION_DECIDED", decision)
        return decision

    def _llm_generate_response(self, belief: dict, decision: dict) -> str:
        self._log("LLM_RESPONSE_GENERATION", {"decision_context": decision})
        action = decision.get("action", "general_response")

        templates = {
            "request_proof": (
                "Halo, gua mengerti banget kekecewaan lu. "
                "Agar bisa langsung gua proses, bisa tolong kirimkan foto kerusakan tersebut di chat ini?"
            ),
            "escalate_to_human": (
                "Halo, gua catat keluhan lu. Karena nilai barangnya cukup tinggi, "
                "sistem gua akan meneruskan kasus lu ke supervisor khusus manusia dalam 1x24 jam "
                "untuk penanganan prioritas."
            ),
            "reject_out_of_warranty": (
                f"Halo, gua mohon maaf. Masa garansi retur sudah melewati batas "
                f"{self.rules['max_auto_refund_days']} hari. "
                f"Gua bisa bantu arahkan ke layanan servis purna jual?"
            ),
            "approve_auto_refund": (
                "Kabar baik! Klaim retur lu sudah gua setujui. "
                "Refund akan diproses dalam 3-5 hari kerja."
            ),
            "general_response": "Halo, ada yang bisa gua bantu?",
        }

        response = templates.get(action, templates["general_response"])
        self._log("RESPONSE_GENERATED", {"action": action, "response": response})
        return response

    def process(self, user_input: str):
        self.audit_log = []
        self.last_error = None

        try:
            belief = self._llm_extract_belief(user_input)
            decision = self._bdi_evaluate_intention(belief)
            response = self._llm_generate_response(belief, decision)
            return response, belief, decision
        except Exception as e:
            self.last_error = {"error": str(e), "traceback": traceback.format_exc()}
            self._log("PROCESS_FAILED", self.last_error)
            return (
                "Maaf, terjadi kesalahan internal. Tim kami akan segera memeriksa.",
                {
                    "intent": "error",
                    "emotion_score": 0,
                    "days_since_purchase": 0,
                    "has_proof": False,
                    "estimated_value": 0,
                },
                {"action": "error", "reason": str(e), "escalate_to_human": True},
            )


# ==================== UI HELPERS ====================


def render_user_message(content: str):
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#3b82f6,#2563eb);'
        f'padding:1rem;border-radius:12px;margin:1rem 20% 1rem 0;color:white">'
        f"<strong>👤 Anda:</strong><br>{content}</div>",
        unsafe_allow_html=True,
    )


def render_assistant_message(content: str):
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#f8fafc,#e2e8f0);'
        f"padding:1rem;border-radius:12px;margin:1rem 0 1rem 20%;color:#1e293b;"
        f'border:2px solid #94a3b8">'
        f"<strong>🤖 Layan Agent:</strong><br>{content}</div>",
        unsafe_allow_html=True,
    )
