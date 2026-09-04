import streamlit as st

st.set_page_config(
    page_title="Layan Care", page_icon="💬", layout="wide", initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown(
    """
<style>
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #1e40af;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .feature-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
        text-align: center;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #64748b;
        font-size: 0.95rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ===== HERO SECTION =====
st.markdown('<div class="hero-title">💬 Layan Care</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Asisten Customer Service Pintar untuk Klaim Retur & Layanan Pelanggan</div>',
    unsafe_allow_html=True,
)

st.write("")

# ===== CTA BUTTON =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.link_button(
        "🚀 Mulai Chat dengan Layan",
        "Layan_Care",  # akan mengarah ke halaman chat
        use_container_width=True,
        type="primary",
    )

st.write("")
st.divider()

# ===== LAYANAN YANG DITAWARKAN =====
st.markdown("### ✨ Layanan yang Kami Tawarkan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">📦</div>
        <div class="feature-title">Klaim Retur Barang Rusak</div>
        <div class="feature-desc">
            Laporkan barang rusak dengan mudah. Sistem akan otomatis mengecek syarat retur.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Proses Cepat & Otomatis</div>
        <div class="feature-desc">
            Klaim yang memenuhi syarat bisa langsung disetujui tanpa menunggu lama.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <div class="feature-title">Pengawasan Human Agent</div>
        <div class="feature-desc">
            Kasus bernilai tinggi atau kompleks akan diteruskan ke supervisor manusia.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")
st.write("")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">📸</div>
        <div class="feature-title">Verifikasi Bukti Foto</div>
        <div class="feature-desc">
            Kirim foto kerusakan untuk mempercepat proses validasi klaim.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">AI + Rule Engine</div>
        <div class="feature-desc">
            Kombinasi LLM dan aturan bisnis membuat keputusan lebih akurat dan transparan.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col6:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon">🕒</div>
        <div class="feature-title">Tersedia 24/7</div>
        <div class="feature-desc">
            Layan siap membantu kapan saja tanpa batasan jam kerja.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# ===== CARA KERJA =====
st.markdown("### 🔄 Cara Kerja Singkat")

st.markdown("""
1. **Ceritakan keluhanmu** — Ketik atau pilih opsi cepat  
2. **Layan menganalisis** — Sistem membaca intent, emosi, dan detail klaim  
3. **Keputusan otomatis** — Approve / Minta bukti / Eskalasi ke manusia  
4. **Selesai** — Kamu langsung dapat jawaban yang jelas
""")

st.write("")
st.divider()

# ===== FOOTER =====
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.9rem;'>"
    "Powered by Groq LLM + BDI Guardrails · Dibuat untuk pengalaman customer service yang lebih baik"
    "</div>",
    unsafe_allow_html=True,
)
