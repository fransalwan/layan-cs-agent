#  Layan CS Agent
**Asisten Customer Service Pintar untuk Klaim Retur & Layanan Pelanggan**

Sebuah implementasi *Hybrid Neuro-Symbolic AI* untuk customer service enterprise yang menggabungkan empati *Large Language Model* (LLM) dengan keandalan sistem berbasis aturan (BDI/Rule Engine), disajikan dalam antarmuka interaktif Streamlit.

---

## 🎯 Tentang Project

**Layan** (bahasa Indonesia: "melayani") adalah agen customer service cerdas yang dirancang untuk menangani permintaan pelanggan dengan pendekatan unik:
1. **Empati & Pemahaman Konteks** (via LLM Layer - Groq/Llama 3)
2. **Kepatuhan & Keamanan** (via BDI/Rule Engine Layer)
3. **Transparansi Penuh** (via Glass-Box Audit Trail)
4. **Antarmuka Interaktif** (via Streamlit Multi-page)

Project ini adalah MVP (*Minimum Viable Product*) yang berfokus pada satu use case utama: **Penanganan Klaim Retur Barang Rusak**.

---

##  Fitur Utama

- **Deep Context Understanding:** Mendeteksi emosi, urgensi, dan mengekstrak informasi penting dari percakapan natural bahasa Indonesia (formal, kasual, hingga slang).
- **Guardrailed Decision Making:** Setiap keputusan divalidasi oleh aturan bisnis yang ketat. Mencegah LLM melakukan "halusinasi" dalam eksekusi kritis (seperti approval refund).
- **Glass-Box Audit Trail:** Setiap interaksi dicatat dengan timestamp dan reasoning yang jelas (*Explainable AI*).
- **Interactive Streamlit UI:** Chat interface modern dengan *Quick Replies* dan panel analisis detail.
- **Empathetic Response Generation:** Respons yang natural, empatik, dan solutif, menyesuaikan gaya komunikasi dengan emosi pelanggan.

---

## 🏗️ Arsitektur & Tech Stack

Project ini menggunakan arsitektur **Hybrid Neuro-Symbolic**:
- **Frontend / UI:** [Streamlit](https://streamlit.io/) (Python)
- **LLM Engine:** [Groq API](https://console.groq.com/) (Model: `llama3-8b-8192`)
- **Logic / Rules:** Python Native (BDI / Rule-based Engine)

---

## 📋 Aturan Bisnis (MVP Scope)

Sistem saat ini mengimplementasikan aturan bisnis berikut untuk Klaim Retur:
✅ Retur hanya diterima dalam **14 hari** sejak pembelian.
✅ **Wajib** melampirkan bukti foto kerusakan (simulasi via chat).
✅ Refund otomatis maksimal **Rp 5.000.000** (di atas itu eskalasi ke manusia).
✅ Semua keputusan dicatat dalam audit log yang dapat diakses.

---

## 🚀 Cara Menjalankan

### 1. Prasyarat
- Python 3.9 atau lebih tinggi
- Akun [Groq Console](https://console.groq.com/) untuk mendapatkan API Key (Gratis).

### 2. Instalasi
Clone repository ini dan buat virtual environment:
```bash
git clone <repository-url>
cd layan-cs-agent

# Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate  # Untuk Mac/Linux
venv\Scripts\activate     # Untuk Windows

# Install dependencies
pip install -r requirements.txt