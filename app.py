import json
import re
import time
from datetime import datetime

import streamlit as st
from groq import Groq


def validate_and_fix_belief(belief: dict, user_input: str) -> dict:
    """Post-processing validation untuk memperbaiki angka & field yang salah dari LLM."""
    input_lower = user_input.lower()

    # --- Fix days_since_purchase ---
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

    # --- Fix estimated_value ---
    value_patterns = [
        (r"(?:rp\.?\s*)?(\d+)\s*(?:jt|juta)", lambda m: int(m.group(1)) * 1_000_000),
        (r"(?:rp\.?\s*)?(\d+)\s*(?:rb|ribu)", lambda m: int(m.group(1)) * 1_000),
        (
            r"(?:rp\.?\s*)?(\d{1,3}(?:[.,]\d{3})+)",
            lambda m: int(re.sub(r"[.,]", "", m.group(1))),
        ),
    ]
    for pattern, extractor in value_patterns:
        match = re.search(pattern, input_lower)
        if match:
            belief["estimated_value"] = extractor(match)
            break

    # --- Fix has_proof ---
    proof_keywords = ["foto", "gambar", "bukti", "photo", "picture", "screenshot", "ss"]
    if any(word in input_lower for word in proof_keywords):
        belief["has_proof"] = True

    # --- Fix emotion_score ---
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
    return Groq(api_key=api_key)


class LayanAgent:
    def __init__(self):
        self.audit_log = []
        self.rules = {
            "max_auto_refund_days": 14,
            "max_auto_refund_amount": 5_000_000,
            "requires_proof_for_damage": True,
        }

    def _log(self, stage, details):
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
        "estimated_value": integer (in Rupiah, 0 if not mentioned)
        }

        Rules:
        - days_since_purchase: convert "minggu" → *7, "bulan" → *30
        - estimated_value: convert "juta/jt" → *1000000, "ribu/rb" → *1000
        - has_proof: true only if user mentions foto/gambar/bukti
        - emotion_score: 8-10 if angry/frustrated words appear
        """

        try:
            client = get_groq_client()
            completion = client.chat.completions.create(
                model="groq/compound",  # model yang lebih stabil
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            belief = json.loads(completion.choices[0].message.content)

            # Post-processing: perbaiki angka yang mungkin salah
            belief = validate_and_fix_belief(belief, user_input)

            self._log("BELIEF_STATE_CREATED", belief)
            return belief

        except Exception as e:
            self._log("LLM_FALLBACK_TRIGGERED", {"error": str(e)})
            return self._fallback_rule_based_parser(user_input)

    def _fallback_rule_based_parser(self, user_input: str) -> dict:
        """Parser rule-based murni jika LLM gagal."""
        input_lower = user_input.lower()

        # Default aman
        days = 0
        value = 0
        emotion = 5
        has_proof = False

        # Ekstrak hari
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

        # Ekstrak nilai
        for pattern, extractor in [
            (
                r"(?:rp\.?\s*)?(\d+)\s*(?:jt|juta)",
                lambda m: int(m.group(1)) * 1_000_000,
            ),
            (r"(?:rp\.?\s*)?(\d+)\s*(?:rb|ribu)", lambda m: int(m.group(1)) * 1_000),
        ]:
            match = re.search(pattern, input_lower)
            if match:
                value = extractor(match)
                break

        # Emotion
        if any(w in input_lower for w in ["gila", "kacau", "parah", "marah", "kesal", "ngamuk"]):
            emotion = 8

        # Proof
        if any(w in input_lower for w in ["foto", "gambar", "bukti", "photo", "screenshot"]):
            has_proof = True

        # Intent
        if any(w in input_lower for w in ["retak", "rusak", "pecah", "defect", "cacat"]):
            return {
                "intent": "request_return_defective",
                "emotion_score": emotion,
                "days_since_purchase": days,
                "has_proof": has_proof,
                "estimated_value": value,
            }

        return {
            "intent": "general_inquiry",
            "emotion_score": 3,
            "days_since_purchase": 0,
            "has_proof": False,
            "estimated_value": 0,
        }

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

        if decision["action"] == "request_proof":
            return (
                "Halo, gua mengerti banget kekecewaan lu. "
                "Agar bisa langsung gua proses, bisa tolong kirimkan foto kerusakan tersebut di chat ini?"
            )
        elif decision["action"] == "escalate_to_human":
            return (
                "Halo, gua catat keluhan lu. Karena nilai barangnya cukup tinggi, "
                "sistem gua akan meneruskan kasus lu ke supervisor khusus manusia dalam 1x24 jam "
                "untuk penanganan prioritas."
            )
        elif decision["action"] == "reject_out_of_warranty":
            return (
                f"Halo, gua mohon maaf. Masa garansi retur sudah melewati batas "
                f"{self.rules['max_auto_refund_days']} hari. "
                f"Gua bisa bantu arahkan ke layanan servis purna jual?"
            )
        elif decision["action"] == "approve_auto_refund":
            return (
                "Kabar baik! Klaim retur lu sudah gua setujui. "
                "Refund akan diproses dalam 3-5 hari kerja."
            )
        else:
            return "Halo, ada yang bisa gua bantu?"

    def process(self, user_input: str):
        self.audit_log = []
        belief = self._llm_extract_belief(user_input)
        decision = self._bdi_evaluate_intention(belief)
        response = self._llm_generate_response(belief, decision)
        return response, belief, decision


# ==================== STREAMLIT UI ====================
st.set_page_config(page_title="Layan CS Agent", page_icon="🤖", layout="wide")

st.markdown(
    '<div style="font-size:2.5rem;font-weight:700;color:#60a5fa;text-align:center">🤖 LAYAN CS AGENT</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="font-size:1.1rem;color:#cbd5e1;text-align:center;margin-bottom:2rem">'
    "Your Personal Customer Service Agent<br>"
    "<i>Powered by Real LLM (Groq) + BDI Guardrails</i></div>",
    unsafe_allow_html=True,
)

if "agent" not in st.session_state:
    st.session_state.agent = LayanAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_belief" not in st.session_state:
    st.session_state.last_belief = None
if "last_decision" not in st.session_state:
    st.session_state.last_decision = None

with st.sidebar:
    st.header("📊 System Info")
    st.markdown(
        "**Arsitektur:** Hybrid Neuro-Symbolic\n\n"
        "**Use Case:** Klaim Retur Barang Rusak\n\n"
        "**Status:** ✅ Active"
    )
    st.divider()
    st.header("🔍 Glass-Box Audit Log")
    if st.session_state.agent.audit_log:
        for log in st.session_state.agent.audit_log:
            with st.expander(f"📝 {log['stage']}"):
                st.json(log["details"])
    else:
        st.info("Belum ada aktivitas.")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = LayanAgent()
        st.rerun()

st.divider()

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#3b82f6,#2563eb);'
            f'padding:1rem;border-radius:12px;margin:1rem 20% 1rem 0;color:white">'
            f"<strong>👤 Anda:</strong><br>{message['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#f8fafc,#e2e8f0);'
            f"padding:1rem;border-radius:12px;margin:1rem 0 1rem 20%;color:#1e293b;"
            f'border:2px solid #94a3b8">'
            f"<strong>🤖 Layan Agent:</strong><br>{message['content']}</div>",
            unsafe_allow_html=True,
        )

        st.divider()
        st.subheader("🧪 Quick Test Scenarios")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📱 Barang Rusak (Baru)", use_container_width=True, type="primary"):
        st.session_state.test_input = (
            "Bro, laptop yang gua beli minggu lalu layarnya retak pas dibuka. Ini kacau banget."
        )
        st.rerun()

with col2:
    if st.button("⏰ Sudah Lewat Garansi", use_container_width=True, type="primary"):
        st.session_state.test_input = (
            "Gua mau retur hp yang layarnya pecah, soalnya beli 3 minggu lalu."
        )
        st.rerun()

with col3:
    if st.button("💰 Nilai Tinggi", use_container_width=True, type="primary"):
        st.session_state.test_input = "HP flagship gua yang 20 juta rusak, baru beli 5 hari lalu."
        st.rerun()

user_input = None
if "test_input" in st.session_state:
    user_input = st.session_state.test_input
    del st.session_state.test_input
else:
    user_text = st.chat_input("Ketik keluhan Anda di sini...")
    if user_text:
        user_input = user_text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("🤔 Layan sedang menganalisis..."):
        time.sleep(0.3)
        response, belief, decision = st.session_state.agent.process(user_input)
        st.session_state.last_belief = belief
        st.session_state.last_decision = decision
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if st.session_state.last_belief and st.session_state.last_decision:
    st.divider()
    st.subheader("🔬 Detailed Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Belief State (Real LLM Output)")
        st.json(st.session_state.last_belief)

    with col2:
        st.markdown("### 🛡️ Decision (BDI Rule Engine)")
        st.json(st.session_state.last_decision)
        action = st.session_state.last_decision["action"]
        if action == "request_proof":
            st.warning("⚠️ Menunggu bukti dari user")
        elif action == "approve_auto_refund":
            st.success("✅ Disetujui - Refund otomatis")
        elif action == "escalate_to_human":
            st.error("🔴 Perlu eskalasi ke manusia")
        elif action == "reject_out_of_warranty":
            st.error("❌ Ditolak - Melebihi garansi")
