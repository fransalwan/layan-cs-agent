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
    /* Animasi fade-in untuk Glass Box */
    .glass-box {
        animation: fadeIn 0.4s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
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
            "content": "Halo! Saya Layan  Ada yang bisa saya bantu hari ini? Silakan ceritakan keluhan kamu.",
            "belief": None,
            "decision": None,
        }
    ]

if "agent" not in st.session_state:
    st.session_state.agent = LayanAgent()


# ===== GLASS-BOX UI COMPONENT =====
def render_claim_status_card(belief, decision):
    """Merender kartu transparan yang menjelaskan keputusan AI."""
    if not belief or not decision:
        return

    action = decision.get("action", "unknown")

    # Mapping status, warna, dan ikon
    status_map = {
        "approve_auto_refund": (
            "#10b981",
            "✅",
            "Klaim Disetujui Otomatis",
            "Refund akan diproses dalam 3-5 hari kerja.",
        ),
        "request_proof": (
            "#f59e0b",
            "",
            "Menunggu Bukti Foto",
            "Sistem memerlukan verifikasi visual sebelum memproses refund.",
        ),
        "escalate_to_human": (
            "#3b82f6",
            "👨‍💼",
            "Diteruskan ke Supervisor",
            "Nilai klaim tinggi, butuh verifikasi manusia dalam 1x24 jam.",
        ),
        "reject_out_of_warranty": (
            "#ef4444",
            "⏰",
            "Masa Garansi Habis",
            "Melebihi batas waktu retur yang ditentukan.",
        ),
        "general_response": (
            "#64748b",
            "💬",
            "Percakapan Umum",
            "Tidak ada tindakan klaim spesifik.",
        ),
    }

    color, icon, title, desc = status_map.get(
        action, ("#64748b", "ℹ️", "Status Tidak Diketahui", "")
    )

    # Format data belief untuk ditampilkan
    emotion_score = belief.get("emotion_score", 5)
    emotion_text = (
        "Tenang" if emotion_score <= 4 else ("Normal" if emotion_score <= 7 else "Tinggi/Marah")
    )

    value = belief.get("estimated_value", 0)
    value_text = f"Rp {value:,}".replace(",", ".") if value > 0 else "Tidak disebutkan"

    days = belief.get("days_since_purchase", 0)
    days_text = f"{days} hari" if days > 0 else "Tidak disebutkan"

    html = f"""
    <div class="glass-box" style="background: #ffffff; border-left: 5px solid {color}; border-radius: 8px; padding: 12px 16px; margin: 0 15% 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: sans-serif;">
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 1.2rem; margin-right: 8px;">{icon}</span>
            <strong style="color: {color}; font-size: 0.95rem;">{title}</strong>
        </div>
        <div style="color: #475569; font-size: 0.85rem; margin-bottom: 10px;">
            {desc} <br> 
            <i style="color: #94a3b8; font-size: 0.8rem;">💡 Alasan sistem: "{decision.get("reason", "")}"</i>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; background: #f8fafc; padding: 8px; border-radius: 6px; font-size: 0.75rem; color: #64748b; text-align: center;">
            <div>📅 <b>Hari Beli</b><br>{days_text}</div>
            <div>💰 <b>Est. Nilai</b><br>{value_text}</div>
            <div>😡 <b>Emosi</b><br>{emotion_text}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ===== TAMPILKAN CHAT =====
for msg in st.session_state.messages:
    if msg["role"] == "user":  # PERBAIKAN: Hapus spasi di "role "
        st.markdown(
            f'<div class="user-bubble"><b>Anda</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bot-bubble"><b>Layan</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        # Tampilkan Glass-Box UI jika ada data belief & decision
        if msg.get("belief") and msg.get("decision"):
            render_claim_status_card(msg["belief"], msg["decision"])

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
        # PERBAIKAN: Hapus spasi di f "qr_{i} "
        if st.button(label, use_container_width=True, key=f"qr_{i}"):
            st.session_state.messages.append({"role": "user", "content": text})
            with st.spinner("Layan sedang membalas..."):
                response, belief, decision = st.session_state.agent.process(text)
                # PERBAIKAN: Simpan belief dan decision ke session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                        "belief": belief,
                        "decision": decision,
                    }
                )
            st.rerun()

# ===== CHAT INPUT =====
user_input = st.chat_input("Ketik pesan kamu di sini...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Layan sedang membalas..."):
        response, belief, decision = st.session_state.agent.process(user_input)
        # PERBAIKAN: Simpan belief dan decision ke session state
        st.session_state.messages.append(
            {"role": "assistant", "content": response, "belief": belief, "decision": decision}
        )
    st.rerun()
