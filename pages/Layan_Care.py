import streamlit as st

from agent import LayanAgent

st.set_page_config(
    page_title="Layan Care",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===== CUSTOM CSS =====
st.markdown(
    """
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.8rem;
    }
    .user-bubble {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.6rem 0 0.6rem 15%;
        text-align: left;
    }
    .bot-bubble {
        background: #f8fafc;
        color: #1e293b;
        padding: 0.9rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.6rem 15% 0.6rem 0;
        border: 1px solid #e2e8f0;
    }
    .stButton > button {
        border-radius: 12px;
        height: 2.8rem;
        font-size: 0.9rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ===== HEADER =====
st.markdown('<div class="main-title">💬 Layan Care</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Customer Service yang siap bantu kamu</div>',
    unsafe_allow_html=True,
)

# ===== SESSION STATE =====
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo! Saya Layan 😊 Ada yang bisa saya bantu hari ini? Silakan ceritakan keluhan kamu.",
        }
    ]

if "agent" not in st.session_state:
    st.session_state.agent = LayanAgent()

# ===== TAMPILKAN CHAT =====
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble"><b>Anda</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bot-bubble"><b>Layan</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

st.write("")

# ===== QUICK REPLIES =====
st.caption("Pilihan cepat:")

quick_replies = [
    ("📱 Barang Rusak", "Barang yang saya beli rusak, layarnya retak."),
    ("⏰ Sudah lewat 2 minggu", "Saya beli barangnya 3 minggu yang lalu, sekarang rusak."),
    ("💰 Barang mahal", "HP saya yang harganya 18 juta rusak."),
    ("📷 Sudah ada foto", "Saya sudah punya foto kerusakannya."),
]

cols = st.columns(4)
for i, (label, text) in enumerate(quick_replies):
    with cols[i]:
        if st.button(label, use_container_width=True, key=f"qr_{i}"):
            st.session_state.messages.append({"role": "user", "content": text})
            with st.spinner("Layan sedang membalas..."):
                response, belief, decision = st.session_state.agent.process(text)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# ===== CHAT INPUT =====
user_input = st.chat_input("Ketik pesan kamu di sini...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Layan sedang membalas..."):
        response, belief, decision = st.session_state.agent.process(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
