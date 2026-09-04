import streamlit as st

st.set_page_config(
    page_title="Layan Care", page_icon="💬", layout="wide", initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown(
    """
    <style>
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
        border-radius: 20px;
        padding: 3rem 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1e40af;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    
    /* Feature Cards with Hover Effect */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Trust Metrics */
    .metric-card {
        text-align: center;
        padding: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1e40af;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.2rem;
    }

    /* How it Works Steps */
    .step-container {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .step-card {
        flex: 1;
        min-width: 200px;
        background: #f1f5f9;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        border-left: 4px solid #3b82f6;
    }
    .step-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #3b82f6;
        margin-bottom: 0.5rem;
    }
    .step-title {
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }
    .step-desc {
        font-size: 0.85rem;
        color: #64748b;
    }

    /* Button Styling Fix untuk Col2 */
    div[data-testid="column"] button[kind="primary"] {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.8rem 1.5rem;
        background-color: #2563eb !important;
        border: none !important;
        color: white !important;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    div[data-testid="column"] button[kind="primary"]:hover {
        transform: scale(1.02);
        background-color: #1d4ed8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== HERO SECTION =====
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">💬 Layan Care</div>
        <div class="hero-subtitle">Asisten Customer Service Pintar untuk Klaim Retur & Layanan Pelanggan</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===== TRUST METRICS =====
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(
        '<div class="metric-card"><p class="metric-value">< 2 Detik</p><p class="metric-label">Waktu Respon AI</p></div>',
        unsafe_allow_html=True,
    )
with col_m2:
    st.markdown(
        '<div class="metric-card"><p class="metric-value">24/7</p><p class="metric-label">Tanpa Libur</p></div>',
        unsafe_allow_html=True,
    )
with col_m3:
    st.markdown(
        '<div class="metric-card"><p class="metric-value">100%</p><p class="metric-label">Transparan & Terukur</p></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ===== CTA BUTTON (FIXED: Menggunakan st.button + st.switch_page) =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(
        "🚀 Mulai Chat dengan Layan", use_container_width=True, type="primary", key="cta_main"
    ):
        st.switch_page("pages/Layan_Care.py")

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
            <div class="feature-desc">Laporkan barang rusak dengan mudah. Sistem akan otomatis mengecek syarat retur.</div>
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
            <div class="feature-desc">Klaim yang memenuhi syarat bisa langsung disetujui tanpa menunggu lama.</div>
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
            <div class="feature-desc">Kasus bernilai tinggi atau kompleks akan diteruskan ke supervisor manusia.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📸</div>
            <div class="feature-title">Verifikasi Bukti Foto</div>
            <div class="feature-desc">Kirim foto kerusakan untuk mempercepat proses validasi klaim.</div>
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
            <div class="feature-desc">Kombinasi LLM dan aturan bisnis membuat keputusan lebih akurat dan transparan.</div>
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
            <div class="feature-desc">Layan siap membantu kapan saja tanpa batasan jam kerja.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# ===== CARA KERJA (VISUAL) =====
st.markdown("### 🔄 Cara Kerja Singkat")

st.markdown(
    """
    <div class="step-container">
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Ceritakan Keluhan</div>
            <div class="step-desc">Ketik atau pilih opsi cepat di chat.</div>
        </div>
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Layan Menganalisis</div>
            <div class="step-desc">AI membaca intent, emosi, dan detail klaim.</div>
        </div>
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Keputusan Otomatis</div>
            <div class="step-desc">Approve / Minta bukti / Eskalasi ke manusia.</div>
        </div>
        <div class="step-card">
            <div class="step-number">4</div>
            <div class="step-title">Selesai</div>
            <div class="step-desc">Kamu langsung dapat jawaban yang jelas.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.divider()

# ===== FOOTER =====
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f1:
    st.markdown(
        "<div style='text-align:left; color:#94a3b8; font-size:0.85rem;'>"
        "Powered by Groq LLM + BDI Guardrails"
        "</div>",
        unsafe_allow_html=True,
    )

with col_f2:
    pass  # Spacer

with col_f3:
    # Tombol ke Google Form Saran (Ganti URL dengan link form lu)
    st.markdown(
        """
        <div style="text-align:right;">
            <a href="https://docs.google.com/forms/d/10LjjNoR8soIkmPO4j3v2bDIlAkD_e5I9DMsrw21nRvw/edit" target="_blank" style="color:#3b82f6; text-decoration:none; font-size:0.85rem; font-weight:600;">
                📝 Beri Saran & Masukan
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
