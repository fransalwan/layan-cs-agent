import streamlit as st
import json
from datetime import datetime
import time

# ============================================
# CLASS LAYAN AGENT (Core Logic - Sama seperti main.py)
# ============================================
class LayanAgent:
    def __init__(self):
        self.audit_log = []
        # Aturan bisnis enterprise (Simbolik/BDI)
        self.rules = {
            "max_auto_refund_days": 14,
            "max_auto_refund_amount": 5000000,
            "requires_proof_for_damage": True
        }

    def _log(self, stage, details):
        """Glass-Box Audit Trail"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage,
            "details": details
        }
        self.audit_log.append(entry)

    def _llm_extract_belief(self, user_input: str) -> dict:
        """Lapisan 1: PERSEPSI (LLM)"""
        self._log("LLM_PERCEPTION", {"raw_input": user_input})
        
        # Simulasi output LLM - deteksi keyword
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["retak", "rusak", "pecah", "damage"]):
            belief = {
                "intent": "request_return_defective",
                "emotion_score": 8 if any(word in input_lower for word in ["kacau", "marah", "jelek", "buruk"]) else 5,
                "days_since_purchase": self._extract_days(input_lower),
                "has_proof": "foto" in input_lower or "gambar" in input_lower or "lampiran" in input_lower,
                "estimated_value": self._extract_value(input_lower)
            }
        else:
            belief = {
                "intent": "general_inquiry",
                "emotion_score": 3,
                "days_since_purchase": 0,
                "has_proof": False,
                "estimated_value": 0
            }
            
        self._log("BELIEF_STATE_CREATED", belief)
        return belief

    def _extract_days(self, text: str) -> int:
        """Extract estimasi hari dari text"""
        if "minggu lalu" in text or "1 minggu" in text or "satu minggu" in text:
            return 7
        elif "2 minggu" in text or "dua minggu" in text:
            return 14
        elif "3 minggu" in text or "tiga minggu" in text:
            return 21
        elif "hari" in text:
            # Coba extract angka
            import re
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 7
        else:
            return 7  # default

    def _extract_value(self, text: str) -> int:
        """Extract estimasi nilai dari text"""
        import re
        if "20 juta" in text or "20000000" in text:
            return 20000000
        elif "15 juta" in text or "15000000" in text:
            return 15000000
        elif "10 juta" in text or "10000000" in text:
            return 10000000
        elif "5 juta" in text or "5000000" in text:
            return 5000000
        elif "3 juta" in text or "3000000" in text:
            return 3000000
        else:
            # Coba extract angka dari text
            numbers = re.findall(r'\d+', text)
            if numbers:
                val = int(numbers[0])
                return val if val > 1000 else val * 1000  # Asumsi dalam ribuan
            return 5000000  # default

    def _bdi_evaluate_intention(self, belief: dict) -> dict:
        """Lapisan 2: PENALARAN & GUARDRAIL (BDI / Rule Engine)"""
        self._log("BDI_RULE_EVALUATION_START", {"checking_rules_against": belief})
        
        decision = {"action": "unknown", "reason": "", "escalate_to_human": False}

        if belief["intent"] == "request_return_defective":
            # Rule 1: Cek batas waktu
            if belief["days_since_purchase"] > self.rules["max_auto_refund_days"]:
                decision["action"] = "reject_out_of_warranty"
                decision["reason"] = f"Melebihi batas {self.rules['max_auto_refund_days']} hari."
            
            # Rule 2: Cek bukti kerusakan
            elif self.rules["requires_proof_for_damage"] and not belief["has_proof"]:
                decision["action"] = "request_proof"
                decision["reason"] = "Bukti kerusakan (foto) wajib dilampirkan sebelum proses refund."
            
            # Rule 3: Cek batas nilai otorisasi bot
            elif belief["estimated_value"] > self.rules["max_auto_refund_amount"]:
                decision["action"] = "escalate_to_human"
                decision["escalate_to_human"] = True
                decision["reason"] = f"Nilai estimasi ({belief['estimated_value']:,}) melebihi batas otorisasi bot ({self.rules['max_auto_refund_amount']:,})."
            
            else:
                decision["action"] = "approve_auto_refund"
                decision["reason"] = "Semua syarat terpenuhi."
                
        self._log("INTENTION_DECIDED", decision)
        return decision

    def _llm_generate_response(self, belief: dict, decision: dict) -> str:
        """Lapisan 3: EKSEKUSI & EMPATI (LLM Kembali)"""
        self._log("LLM_RESPONSE_GENERATION", {"decision_context": decision})
        
        if decision["action"] == "request_proof":
            return (
                "Halo, gua mengerti banget kekecewaan lu, apalagi barangnya baru. "
                "Agar bisa langsung gua proses pengembaliannya, bisa tolong kirimkan foto kerusakan tersebut di chat ini? "
                "Setelah itu, gua akan bantu percepat prosesnya."
            )
        elif decision["action"] == "escalate_to_human":
            return (
                "Halo, gua catat keluhan lu terkait kerusakan ini. "
                "Karena nilai barangnya cukup tinggi, sistem gua secara otomatis akan meneruskan kasus lu ke supervisor khusus manusia "
                "dalam 1x24 jam untuk penanganan prioritas dan verifikasi refund yang lebih aman. Terima kasih sudah bersabar."
            )
        elif decision["action"] == "reject_out_of_warranty":
            return (
                "Halo, gua mohon maaf atas ketidaknyamanan ini. "
                f"Berdasarkan data, masa garansi retur untuk barang ini sudah melewati batas {self.rules['max_auto_refund_days']} hari. "
                "Gua bisa bantu arahkan ke layanan servis purna jual untuk opsi perbaikan?"
            )
        elif decision["action"] == "approve_auto_refund":
            return (
                "Kabar baik! Klaim retur lu sudah gua setujui. "
                "Refund akan diproses dalam 3-5 hari kerja ke rekening yang terdaftar. "
                "Gua juga sudah kirimkan label pengiriman via email. Ada yang bisa gua bantu lagi?"
            )
        else:
            return "Halo, ada yang bisa gua bantu terkait pesanan lu?"

    def process(self, user_input: str):
        """Main processing pipeline"""
        # Clear audit log untuk session baru
        self.audit_log = []
        
        # 1. Belief
        belief = self._llm_extract_belief(user_input)
        
        # 2. Intention (Desire di-filter oleh Rules)
        decision = self._bdi_evaluate_intention(belief)
        
        # 3. Response
        response = self._llm_generate_response(belief, decision)
        
        return response, belief, decision

# ============================================
# STREAMLIT UI
# ============================================

st.set_page_config(
    page_title="Layan CS Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Improved Contrast & Visibility
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #60a5fa;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.1rem;
        color: #cbd5e1;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Chat Messages - High Contrast */
    .chat-message {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .user-message {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        margin-left: 20%;
        color: #ffffff;
        border: 2px solid #60a5fa;
    }
    .user-message strong {
        color: #ffffff;
        font-size: 1rem;
    }
    .user-message div {
        color: #ffffff;
        font-size: 1rem;
        line-height: 1.5;
    }
    .agent-message {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        margin-right: 20%;
        color: #1e293b;
        border: 2px solid #94a3b8;
    }
    .agent-message strong {
        color: #0f172a;
        font-size: 1rem;
    }
    .agent-message div {
        color: #1e293b;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Buttons - High Visibility */
    .stButton>button {
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Chat Input */
    .stChatInput>div>input {
        background-color: #1e293b;
        color: #ffffff;
        border: 2px solid #475569;
        border-radius: 8px;
        padding: 0.8rem;
    }
    .stChatInput>div>input:focus {
        border-color: #60a5fa;
    }
    .stChatInput>div>input::placeholder {
        color: #94a3b8;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 2px solid #334155;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #60a5fa;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        color: #cbd5e1;
    }
    
    /* Expander for Audit Log */
    .streamlit-expanderHeader {
        background-color: #334155;
        color: #60a5fa;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem;
    }
    .streamlit-expanderContent {
        background-color: #0f172a;
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 0.8rem;
    }
    
    /* Status Indicators */
    .stAlert {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Dividers */
    hr {
        border-color: #334155;
    }
    
    /* JSON Display */
    .stJson {
        background-color: #0f172a;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 0.8rem;
    }
    
    /* Spinner */
    .stSpinner>div {
        border-color: #60a5fa;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 LAYAN CS AGENT</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Personal Customer Service Agent<br><i>Hybrid Neuro-Symbolic AI for Enterprise</i></div>', unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = LayanAgent()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_belief' not in st.session_state:
    st.session_state.last_belief = None
if 'last_decision' not in st.session_state:
    st.session_state.last_decision = None

# Sidebar - Info & Audit Log
with st.sidebar:
    st.header("📊 System Info")
    st.markdown("""
    **Arsitektur:** Hybrid Neuro-Symbolic  
    **Use Case:** Klaim Retur Barang Rusak  
    **Status:** ✅ Active
    """)
    
    st.divider()
    
    st.header("🔍 Glass-Box Audit Log")
    if st.session_state.agent.audit_log:
        for log in st.session_state.agent.audit_log:
            with st.expander(f"📝 {log['stage']}"):
                st.json(log['details'])
                st.caption(f"⏰ {log['timestamp']}")
    else:
        st.info("Belum ada aktivitas. Silakan kirim pesan untuk melihat audit log.")
    
    st.divider()
    
    if st.button("️ Clear History", type="secondary"):
        st.session_state.messages = []
        st.session_state.agent = LayanAgent()
        st.rerun()

# Main Chat Interface
st.divider()

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div>
                <strong>👤 Anda:</strong><br>
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message agent-message">
            <div>
                <strong>🤖 Layan Agent:</strong><br>
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Quick Test Scenarios
st.divider()
st.subheader("🧪 Quick Test Scenarios")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📱 Barang Rusak (Baru)", use_container_width=True):
        st.session_state.test_input = "Bro, laptop yang gua beli minggu lalu layarnya retak pas dibuka. Ini kacau banget. Gimana cara balikinnya?"
        st.rerun()

with col2:
    if st.button("⏰ Sudah Lewat Garansi", use_container_width=True):
        st.session_state.test_input = "Gua mau retur hp yang layarnya pecah, soalnya beli 3 minggu lalu."
        st.rerun()

with col3:
    if st.button("💰 Nilai Tinggi", use_container_width=True):
        st.session_state.test_input = "HP flagship gua yang 20 juta rusak, baru beli 5 hari lalu. Mau retur gimana?"
        st.rerun()

# Check if there's a test input
if 'test_input' in st.session_state:
    user_input = st.session_state.test_input
    del st.session_state.test_input
else:
    user_input = None

# Chat input
st.divider()
col1, col2 = st.columns([4, 1])

with col1:
    user_text = st.chat_input("Ketik keluhan atau pertanyaan Anda di sini...", key="chat_input")

if user_text:
    user_input = user_text

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show processing indicator
    with st.spinner('🤔 Layan sedang menganalisis...'):
        time.sleep(0.5)  # Simulasi processing
        
        # Process with agent
        response, belief, decision = st.session_state.agent.process(user_input)
        
        # Store belief and decision
        st.session_state.last_belief = belief
        st.session_state.last_decision = decision
    
    # Add agent response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to display new messages
    st.rerun()

# Display detailed analysis if available
if st.session_state.last_belief and st.session_state.last_decision:
    st.divider()
    st.subheader("🔬 Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###  Belief State (LLM Perception)")
        st.json(st.session_state.last_belief)
        
    with col2:
        st.markdown("### 🎯 Decision (BDI Rule Engine)")
        st.json(st.session_state.last_decision)
        
        # Visual indicator
        if st.session_state.last_decision['action'] == 'request_proof':
            st.warning("⚠️ Menunggu bukti dari user")
        elif st.session_state.last_decision['action'] == 'approve_auto_refund':
            st.success("✅ Disetujui - Refund otomatis")
        elif st.session_state.last_decision['action'] == 'escalate_to_human':
            st.error("🔴 Perlu eskalasi ke manusia")
        elif st.session_state.last_decision['action'] == 'reject_out_of_warranty':
            st.error("❌ Ditolak - Melebihi garansi")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><strong>Layan CS Agent</strong> - Melayani dengan Empati, Melindungi dengan Kepastian</p>
    <p>Built with Streamlit & Hybrid Neuro-Symbolic AI Architecture</p>
</div>
""", unsafe_allow_html=True)