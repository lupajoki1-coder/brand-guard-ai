import streamlit as st
import google.generativeai as genai
from googlesearch import search
from fpdf import FPDF
import datetime
import re

# --- 1. KONFIGURASI UI/UX PREMIUM ---
st.set_page_config(
    page_title="KSB Suite Audit", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed" # Tampilan lebih bersih
)

# Inject CSS untuk tampilan Audit Professional (Tables & Cards)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* Base */
    .stApp { background-color: #f1f5f9; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Audit Card */
    .audit-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Tables */
    table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }
    th { background-color: #f8fafc; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #64748b; font-weight: 800; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
    td { padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1e293b; font-weight: 500; }
    
    /* Typography */
    h1 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; letter-spacing: -1px; color: #0f172a; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #0ea5e9; }
    
    /* Button */
    .stButton>button {
        background-color: #0f172a; color: white; border-radius: 8px; 
        font-weight: 600; padding: 0.6rem 2rem; border: none; width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #334155; transform: scale(1.01); }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA REFERENSI (KELAS MEREK SIMPLIFIED) ---
NICE_CLASSES = [
    "03 - Kosmetik & Parfum", "05 - Farmasi & Obat", "09 - Software & Elektronik", 
    "25 - Pakaian & Sepatu", "30 - Kopi, Makanan, Roti", "32 - Minuman Non-Alkohol",
    "35 - Jasa Toko/Retail & Iklan", "41 - Pendidikan & Event", "43 - Restoran & Kafe", 
    "45 - Jasa Hukum & Keamanan", "Lainnya (Tulis Manual di Prompt)"
]

# --- 3. FUNGSI PENDUKUNG ---
def clean_for_pdf(text):
    """Menghapus emoji dan karakter aneh untuk PDF FPDF standard"""
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_audit_pdf(brand, cls, analysis_text, risk_score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # -- Header --
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "TRADEMARK FORENSIC AUDIT", 0, 1, 'C')
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, f"Re: {brand.upper()} ({cls}) | Date: {datetime.date.today()}", 0, 1, 'C')
    pdf.ln(5)
    
    # -- Risk Box --
    pdf.set_fill_color(241, 245, 249) # Slate-100
    pdf.rect(10, 30, 190, 15, 'F')
    pdf.set_y(33)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, f"RISK VERDICT: {risk_score.upper()}", 0, 1, 'C')
    pdf.ln(10)
    
    # -- Body Content (Structured) --
    pdf.set_font("Courier", "", 10) # Monospace agar terlihat seperti laporan teknis
    
    # Kita bersihkan emoji dari teks AI agar PDF tidak error
    clean_body = clean_for_pdf(analysis_text)
    
    # Hapus format markdown tabel garis (|) agar rapi di plain text PDF
    clean_body = clean_body.replace("|", " ").replace("---", "-")
    
    pdf.multi_cell(0, 5, clean_body)
    
    # -- Footer --
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 7)
    pdf.cell(0, 10, "CONFIDENTIAL // KSB SUITE ULTIMA AUTOMATED REPORT", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

def search_pdki_smart(brand_name):
    competitors = []
    try:
        # Search Query yang sangat spesifik ke portal DJKI
        query = f'site:pdki-indonesia.dgip.go.id "{brand_name}" OR {brand_name}'
        for url in search(query, num_results=6, lang="id"):
            competitors.append(url)
    except:
        pass
    return competitors

# --- 4. ENGINE AI (AUDITOR MODE) ---
def run_audit(api_key, brand, cls, competitors):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash") # Menggunakan model tercepat
    
    comp_str = "\n".join(competitors) if competitors else "Nil (Tidak ditemukan di index publik)"
    
    # PROMPT "AUDITOR GALAK" (Tanpa Basa-basi)
    prompt = f"""
    ROLE: Lead Trademark Auditor.
    TONE: Strict, Direct, No-Fluff, Corporate-Audit Style.
    OBJECTIVE: Audit potensi penolakan merek berdasarkan UU Merek No 20 Tahun 2016.

    TARGET: "{brand}" (Kelas {cls})
    DATABASE FINDINGS:
    {comp_str}

    INSTRUCTION:
    1. Abaikan basa-basi pembuka/penutup. Langsung ke inti.
    2. Wajib gunakan format TABEL MARKDOWN untuk analisis.
    3. Gunakan Emoji Indikator: 🔴 (High Risk), 🟡 (Medium Risk), 🟢 (Safe/Low Risk).

    OUTPUT FORMAT:

    ### 1. EXECUTIVE SUMMARY
    [Satu kalimat tajam kesimpulan akhir: LOLOS atau DITOLAK]

    ### 2. FORENSIC MATRIX
    | PARAMETER AUDIT | TEMUAN KRITIS | RISIKO |
    | :--- | :--- | :--- |
    | **Fonetik (Bunyi)** | [Analisis kemiripan bunyi dengan merek terkenal/database. Contoh: 'SANSUNG' vs 'SAMSUNG'] | [Emoji] |
    | **Konseptual (Makna)** | [Analisis arti kata, terjemahan asing, atau makna menyesatkan] | [Emoji] |
    | **Visual (Tampilan)** | [Potensi 'Si Kembar Beda Ibu' jika logo dibuat mirip] | [Emoji] |
    | **Distingsi (Pembeda)** | [Apakah kata ini Generik/Deskriptif? Contoh: 'GULA' untuk produk Gula = Ditolak] | [Emoji] |

    ### 3. REKOMENDASI TAKTIS
    - [Saran 1: Ubah ejaan/tambah kata pembeda]
    - [Saran 2: Strategi Logo]
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 5. ANTARMUKA APLIKASI ---

# Header Section
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='margin-bottom: -10px;'>KSB SUITE <span style='color:#0ea5e9;'>ULTIMA</span></h1>
        <p style='color:#64748b; font-size: 14px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;'>Automated Trademark Forensic</p>
    </div>
""", unsafe_allow_html=True)

# Cek API Key Otomatis
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.warning("⚠️ API Key belum tertanam di Secrets. Aplikasi mungkin tidak berjalan.")
    api_key = st.text_input("Emergency API Input", type="password")

# Container Utama
with st.container():
    # Gunakan Columns untuk layout Input yang rapi
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        brand_input = st.text_input("Target Merek", placeholder="Ketik nama merek...")
    with c2:
        class_input = st.selectbox("Kelas", NICE_CLASSES)
    with c3:
        st.write("") # Spacer
        st.write("") 
        btn_audit = st.button("RUN AUDIT ⚡")

# Logic Eksekusi
if btn_audit:
    if not api_key:
        st.error("Missing Credential: API Key")
    elif not brand_input:
        st.error("Missing Input: Nama Merek")
    else:
        # Progress Bar visual
        progress_text = "Memindai Database PDKI & Melakukan Cross-Check..."
        my_bar = st.progress(0, text=progress_text)
        
        # 1. Searching
        competitors = search_pdki_smart(brand_input)
        my_bar.progress(50, text="Menganalisis Fonetik & Semantik dengan AI...")
        
        # 2. Reasoning
        audit_result = run_audit(api_key, brand_input, class_input, competitors)
        my_bar.progress(100, text="Selesai.")
        my_bar.empty()
        
        # 3. Tampilan Hasil (Card Style)
        st.markdown(f"""
        <div class="audit-card">
            <h3 style="margin-top:0; color:#0f172a; border-bottom: 2px solid #0ea5e9; padding-bottom: 10px; margin-bottom: 20px;">
                AUDIT REPORT: {brand_input.upper()}
            </h3>
            {audit_result}
        </div>
        """, unsafe_allow_html=True)
        
        # 4. PDF Download Logic
        # Tentukan status risiko kasar untuk metadata PDF
        risk_level = "UNKNOWN"
        if "🔴" in audit_result: risk_level = "HIGH RISK"
        elif "🟡" in audit_result: risk_level = "MEDIUM RISK"
        else: risk_level = "LOW RISK / SAFE"
        
        pdf_data = create_audit_pdf(brand_input, class_input, audit_result, risk_level)
        
        c_down1, c_down2 = st.columns([3, 1])
        with c_down2:
            st.download_button(
                label="📥 UNDUH LAPORAN (PDF)",
                data=pdf_data,
                file_name=f"AUDIT_{brand_input.upper()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
