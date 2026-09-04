import time

import streamlit as st

from agent import LayanAgent, render_assistant_message, render_user_message, safe_json

st.set_page_config(page_title="Layan CS Agent - Admin", page_icon="🤖", layout="wide")

st.markdown(
    '<div style="font-size:2.5rem;font-weight:700;color:#60a5fa;text-align:center">🤖 LAYAN CS AGENT</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="font-size:1.1rem;color:#cbd5e1;text-align:center;margin-bottom:2rem">'
    "Admin / Debug Panel<br>"
    "<i>Powered by Real LLM (Groq) + BDI Guardrails</i></div>",
    unsafe_allow_html=True,
)

# Session state
if "agent" not in st.session_state:
    st.session_state.agent = LayanAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_belief" not in st.session_state:
    st.session_state.last_belief = None
if "last_decision" not in st.session_state:
    st.session_state.last_decision = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = True

# ===== SIDEBAR =====
with st.sidebar:
    st.header("📊 System Info")
    st.markdown(
        "**Arsitektur:** Hybrid Neuro-Symbolic\n\n"
        "**Use Case:** Klaim Retur Barang Rusak\n\n"
        "**Model:** `groq/compound`\n\n"
        "**Status:** ✅ Active"
    )

    st.divider()
    st.session_state.debug_mode = st.toggle("🛠️ Debug Mode", value=st.session_state.debug_mode)

    st.divider()
    st.header("🔍 Glass-Box Audit Log")

    if st.session_state.agent.audit_log:
        for log in st.session_state.agent.audit_log:
            with st.expander(f"📝 {log['stage']} — {log['timestamp']}"):
                st.json(log["details"])
    else:
        st.info("Belum ada aktivitas.")

    if st.session_state.debug_mode and st.session_state.agent.last_error:
        st.divider()
        st.error("Last Error")
        st.json(st.session_state.agent.last_error)

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = LayanAgent()
        st.session_state.last_belief = None
        st.session_state.last_decision = None
        st.rerun()

# ===== CHAT HISTORY =====
st.divider()

for message in st.session_state.messages:
    if message["role"] == "user":
        render_user_message(message["content"])
    else:
        render_assistant_message(message["content"])

# ===== QUICK TEST =====
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

# ===== QUICK REPLY =====
st.markdown("#### 💬 Pilihan Cepat")

quick_replies = [
    ("📷 Kirim Foto Kerusakan", "Ini fotonya, barangnya retak di bagian layar."),
    ("😠 Saya Kecewa Banget", "Saya kecewa banget, barangnya rusak parah."),
    ("📅 Baru Beli Kemarin", "Barang ini baru saya beli kemarin."),
    ("💰 Harganya 15 Juta", "Barangnya seharga 15 juta."),
    ("🔄 Mau Tukar Unit", "Saya lebih mau tukar unit daripada refund."),
    ("📞 Hubungi Human Agent", "Tolong hubungkan saya ke customer service manusia."),
]

cols = st.columns(3)
for idx, (label, message) in enumerate(quick_replies):
    with cols[idx % 3]:
        if st.button(label, use_container_width=True, key=f"qr_{idx}"):
            st.session_state.test_input = message
            st.rerun()

# ===== INPUT HANDLING =====
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
        time.sleep(0.2)
        response, belief, decision = st.session_state.agent.process(user_input)
        st.session_state.last_belief = belief
        st.session_state.last_decision = decision
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ===== DETAILED ANALYSIS =====
if st.session_state.last_belief and st.session_state.last_decision:
    st.divider()
    st.subheader("🔬 Detailed Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Belief State")
        st.json(safe_json(st.session_state.last_belief))

    with col2:
        st.markdown("### 🛡️ Decision (BDI)")
        st.json(safe_json(st.session_state.last_decision))

        action = st.session_state.last_decision.get("action", "")
        if action == "request_proof":
            st.warning("⚠️ Menunggu bukti dari user")
        elif action == "approve_auto_refund":
            st.success("✅ Disetujui - Refund otomatis")
        elif action == "escalate_to_human":
            st.error("🔴 Perlu eskalasi ke manusia")
        elif action == "reject_out_of_warranty":
            st.error("❌ Ditolak - Melebihi garansi")
        elif action == "error":
            st.error("💥 Terjadi error internal")

    if st.session_state.debug_mode:
        st.divider()
        st.subheader("🛠️ Debug Panel")
        st.write("**Jumlah log entries:**", len(st.session_state.agent.audit_log))
        if st.session_state.agent.last_error:
            st.error("Ada error terakhir:")
            st.code(st.session_state.agent.last_error.get("traceback", ""), language="text")
