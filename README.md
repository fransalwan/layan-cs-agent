# 🤖 Layan CS Agent

**Your Personal Customer Service Agent**

Sebuah implementasi **Hybrid Neuro-Symbolic AI** untuk customer service enterprise yang menggabungkan empati Large Language Model (LLM) dengan keandalan sistem berbasis aturan (BDI/Rule Engine), disajikan dalam antarmuka interaktif Streamlit.

---

## 🎯 Tentang Project

**Layan** (bahasa Indonesia: "melayani") adalah agen customer service cerdas yang dirancang untuk menangani permintaan pelanggan dengan pendekatan unik:

- **Empati & Pemahaman Konteks** (via LLM Layer)
- **Kepatuhan & Keamanan** (via BDI/Rule Engine Layer)
- **Transparansi Penuh** (via Glass-Box Audit Trail)
- **Antarmuka Interaktif** (via Streamlit)

Project ini adalah **MVP (Minimum Viable Product)** yang fokus pada satu use case: **Penanganan Klaim Retur Barang Rusak**.

---

## 🌟 Fitur Utama

### 1. **Deep Context Understanding**
- Mendeteksi emosi dan urgensi dari keluhan pelanggan
- Mengekstrak informasi penting dari percakapan natural yang tidak terstruktur
- Memahami nuansa bahasa Indonesia (formal, kasual, bahkan slang)

### 2. **Guardrailed Decision Making**
- Setiap keputusan divalidasi oleh aturan bisnis yang ketat
- Mencegah LLM melakukan "halusinasi" dalam eksekusi kritis (refund, perubahan data)
- Eskalasi otomatis ke manusia untuk kasus berisiko tinggi

### 3. **Glass-Box Audit Trail**
- Setiap interaksi dicatat dengan timestamp dan reasoning yang jelas
- Explainable AI: Anda bisa melacak **mengapa** agen mengambil keputusan tertentu
- Visualisasi real-time di sidebar Streamlit

### 4. **Interactive Streamlit UI**
- Chat interface modern dan responsif
- Quick test scenarios untuk demo cepat
- Detailed analysis panel untuk melihat Belief State dan Decision
- Visual indicators untuk status keputusan

### 5. **Empathetic Response Generation**
- Respons yang natural, empatik, dan solutif
- Menyesuaikan gaya komunikasi dengan emosi pelanggan
- Tidak kaku seperti chatbot tradisional

---

## 🏗️ Arsitektur: Hybrid Neuro-Symbolic


## 📋 MVP Scope

**Use Case:** Penanganan Klaim Retur Barang Rusak

**Aturan Bisnis yang Diimplementasikan:**
1. ✅ Retur hanya diterima dalam 14 hari sejak pembelian
2. ✅ Wajib melampirkan bukti foto kerusakan
3. ✅ Refund otomatis maksimal Rp 5.000.000 (di atas itu eskalasi ke manusia)
4. ✅ Semua keputusan dicatat dalam audit log yang dapat diakses via UI

---

## 🚀 Cara Menjalankan

### Prasyarat
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Instalasi

1. **Clone atau download repository ini**
   ```bash
   git clone <repository-url>
   cd layan-cs-agent