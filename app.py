import streamlit as st
import google.generativeai as genai
import Levenshtein
from googlesearch import search
from fpdf import FPDF
import datetime

# --- 1. KONFIGURASI UI/UX (MENGACU PADA INDEX.HTML) ---
st.set_page_config(
    page_title="KSB Suite v6.0 (Ultima)", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk meniru gaya 'index.html' (Glassmorphism & Fonts)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* Global Style */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            radial-gradient(at 0% 0%, hsla(210, 100%, 93%, 1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(190, 100%, 90%, 1) 0, transparent 50%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Titles */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; color: #0f172a; }
    
    /* Glass Panel Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(to right, #0ea5e9, #0284c7);
        color: white;
        border-radius: 16px;
        font-weight: 700;
        border: none;
        padding: 0.75rem 1.5rem;
        width: 100%;
        box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.3);
        font-family: 'Outfit', sans-serif;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(14, 165, 233, 0.4);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background-color: rgba(255,255,255,0.8);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA REFERENSI (KELAS MEREK LENGKAP) ---
NICE_CLASSES = [
    "Kelas 1: Bahan Kimia Industri", "Kelas 2: Cat & Pernis", "Kelas 3: Kosmetik & Pembersih (Parfum, Skincare)",
    "Kelas 4: Minyak & Bahan Bakar", "Kelas 5: Farmasi & Obat", "Kelas 6: Logam Tidak Mulia",
    "Kelas 7: Mesin & Perkakas", "Kelas 8: Peralatan Tangan", "Kelas 9: Teknologi, Software, Kacamata",
    "Kelas 10: Alat Medis", "Kelas 11: Alat Penerangan & Pemanas", "Kelas 12: Kendaraan",
    "Kelas 13: Senjata Api", "Kelas 14: Perhiasan & Jam", "Kelas 15: Alat Musik",
    "Kelas 16: Kertas & Alat Tulis", "Kelas 17: Karet & Plastik", "Kelas 18: Kulit & Tas",
    "Kelas 19: Bahan Bangunan (Non-Logam)", "Kelas 20: Perabot & Mebel", "Kelas 21: Alat Rumah Tangga & Dapur",
    "Kelas 22: Tali & Jaring", "Kelas 23: Benang", "Kelas 24: Tekstil",
    "Kelas 25: Pakaian, Sepatu, Topi", "Kelas 26: Renda & Bordir", "Kelas 27: Karpet & Alas Lantai",
    "Kelas 28: Mainan & Alat Olahraga", "Kelas 29: Daging, Ikan, Buah Olahan", "Kelas 30: Kopi, Teh, Roti, Beras",
    "Kelas 31: Hasil Pertanian Segar", "Kelas 32: Minuman Non-Alkohol (Air, Jus)", "Kelas 33: Minuman Beralkohol",
    "Kelas 34: Tembakau & Rokok",
    "Kelas 35: Jasa Periklanan & Toko (Retail)", "Kelas 36: Jasa Keuangan & Real Estate",
    "Kelas 37: Jasa Konstruksi & Perbaikan", "Kelas 38: Jasa Telekomunikasi", "Kelas 39: Jasa Transportasi",
    "Kelas 40: Jasa Pengolahan Material", "Kelas 41: Jasa Pendidikan & Hiburan",
    "Kelas 42: Jasa Teknologi & Desain (IT)", "Kelas 43: Jasa Makanan & Minuman (Restoran/Kafe)",
    "Kelas 44: Jasa Medis & Kecantikan", "Kelas 45: Jasa Hukum & Keamanan"
]

# --- 3. FUNGSI SMART LEGAL SEARCH (PDKI) ---
def search_pdki_smart(brand_name):
    """
    Melakukan pencarian cerdas ke index PDKI.
    Mencari Nama Persis DAN Kata Dominan.
    """
    competitors = []
    queries = [
        f'site:pdki-indonesia.dgip.go.id "{brand_name}"', # Exact match
        f'site:pdki-indonesia.dgip.go.id {brand_name}'   # Broad match
    ]
    
    seen_urls = set()
    
    try:
        for q in queries:
            for url in search(q, num_results=5, lang="id"):
                if url not in seen_urls:
                    competitors.append(url)
                    seen_urls.add(url)
    except Exception as e:
        return [f"Error searching: {str(e)}"]
    
    return competitors[:8] # Ambil 8 hasil terbaik

# --- 4. ENGINE PDF GENERATOR (REPORTLAB STYLE) ---
def create_pdf(brand, cls, analysis_text, risk_score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header Styling
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(15, 23, 42) # Slate-900
    pdf.cell(0, 10, "KSB Suite Ultima Report", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(14, 165, 233) # Sky-500
    pdf.cell(0, 8, "FORENSIC TRADEMARK AUDIT", ln=True)
    pdf.ln(5)
    
    # Metadata
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Merek: {brand}", ln=True)
    pdf.cell(0, 6, f"Kelas: {cls}", ln=True)
    pdf.cell(0, 6, f"Tanggal: {datetime.date.today()}", ln=True)
    pdf.cell(0, 6, f"Skor Risiko: {risk_score}", ln=True)
    pdf.line(10, 50, 200, 50)
    pdf.ln(10)
    
    # Body
    pdf.set_font("Arial", "", 11)
    # FPDF tidak support markdown, kita clean text sederhananya
    clean_text = analysis_text.replace("*", "").replace("#", "")
    pdf.multi_cell(0, 6, clean_text)
    
    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Generated by KSB Suite AI - Not Legal Advice", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. LOGIKA AI (GEMINI 2.5 FLASH) ---
def analyze_brand_pro(api_key, model_ver, brand, cls, competitors):
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(model_ver)
    except:
        return "Error Model", "0%"

    comp_list = "\n".join(competitors) if competitors else "Tidak ditemukan merek identik di index publik."

    # PROMPT BERDASARKAN FILE PDF 'TIPS MEREK'
    prompt = f"""
    Bertindaklah sebagai Konsultan HKI Senior (Spesialis Merek Indonesia).
    Lakukan Audit Forensik Merek berdasarkan UU No. 20 Tahun 2016.

    DATA PEMOHON:
    - Nama Merek: "{brand}"
    - Kelas: {cls}
    
    DATA DATABASE (PDKI Index):
    {comp_list}

    TUGAS ANALISIS (GUNAKAN 4 PRINSIP UTAMA):
    
    1. **ANALISIS FONETIK (Bunyi Ucapan)** [PENTING]
       - Apakah ada kemiripan bunyi dengan merek terkenal? (Seperti kasus SANSUNG vs SAMSUNG).
       - Cek pelafalan suku kata dominan.
    
    2. **ANALISIS KONSEPTUAL (Makna)**
       - Apakah ini terjemahan dari merek asing terkenal? (Prinsip RED BULL vs BANTENG MERAH).
       - Apakah memiliki makna yang sama dengan merek lain di kelas yang sama?
    
    3. **ANALISIS VISUAL (Tampilan)**
       - Jika nama ini dibuat logo, apakah teksnya mudah dibedakan atau rawan "Si Kembar Beda Ibu"?
    
    4. **ANALISIS DISTINGSI (Daya Pembeda)**
       - Apakah nama ini terlalu deskriptif/umum? (Contoh: "GULA MANIS" untuk produk gula akan DITOLAK MUTLAK).
       - Apakah ini melanggar ketertiban umum?

    OUTPUT FINAL:
    Berikan kesimpulan tegas: **[PELUANG LOLOS: TINGGI / SEDANG / RENDAH]**.
    Jelaskan alasannya dalam poin-poin singkat dan tajam.
    """

    response = model.generate_content(prompt)
    return response.text

# --- 6. UI UTAMA (MAIN APP) ---

# Sidebar Konfigurasi
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    # API Key Handling (Auto/Manual)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Terhubung")
    else:
        api_key = st.text_input("🔑 Google Gemini API Key", type="password")
        st.caption("[Get API Key](https://aistudio.google.com/app/apikey)")

    st.markdown("---")
    
    # Model Selector
    model_version = st.selectbox(
        "🧠 AI Engine",
        ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
        index=0
    )
    st.info("Mode: Forensic Audit")

# Layout Halaman Utama
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    # Hero Section
    st.markdown("""
    <div class="glass-card">
        <h1 style='color:#0ea5e9; font-size:24px; margin-bottom:5px;'>KSB Suite <span style='font-size:12px; background:#e0f2fe; padding:2px 8px; border-radius:10px;'>ULTIMA</span></h1>
        <h2 style='font-size:32px; font-weight:800; line-height:1.2;'>Forensic Audit<br>Protection.</h2>
        <p style='color:#64748b; font-size:14px; margin-top:10px;'>
            Cek potensi penolakan merek (Fonetik, Visual, Konseptual) sebelum pendaftaran hangus.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Form
    with st.container():
        st.markdown("#### 📝 Data Merek")
        input_brand = st.text_input("Nama Merek", placeholder="Contoh: MANAKALA")
        input_class = st.selectbox("Pilih Kelas (Nice Classification)", NICE_CLASSES)
        
        btn_process = st.button("✨ Jalankan Audit Forensik")

with col2:
    if btn_process:
        if not api_key:
            st.error("⚠️ Masukkan API Key di Sidebar.")
        elif not input_brand:
            st.warning("⚠️ Masukkan Nama Merek.")
        else:
            # 1. Searching
            with st.status("🔍 Memindai Database PDKI & Global...", expanded=True) as status:
                st.write("Mengontak index Google Search...")
                competitors = search_pdki_smart(input_brand)
                st.write(f"Ditemukan {len(competitors)} data pembanding potensial.")
                status.update(label="Scanning Selesai", state="complete", expanded=False)
            
            # 2. AI Reasoning
            with st.spinner("🤖 Melakukan Analisis 4 Dimensi (Fonetik, Visual, Konseptual, Distingsi)..."):
                result_text = analyze_brand_pro(api_key, model_version, input_brand, input_class, competitors)
            
            # 3. Display Result (Card Style)
            st.markdown(f"""
            <div class="glass-card" style="border-left: 5px solid #0ea5e9;">
                <h3 style="margin-top:0;">📊 Hasil Analisis AI</h3>
                <hr style="margin: 10px 0; opacity: 0.2;">
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(result_text)
            
            # 4. PDF Download (Logic)
            # Tentukan skor risiko kasar dari teks untuk metadata PDF
            risk = "HIGH" if "RENDAH" in result_text.upper() else "LOW"
            
            pdf_bytes = create_pdf(input_brand, input_class, result_text, risk)
            
            st.download_button(
                label="📄 Unduh Laporan Resmi (PDF)",
                data=pdf_bytes,
                file_name=f"AUDIT_MEREK_{input_brand.upper()}.pdf",
                mime="application/pdf"
            )

# Footer
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px;'>
    Powered by <b>Gemini 2.5 Flash</b> & <b>PDKI Index</b> | KSB Suite Ultima v6.0
</div>
""", unsafe_allow_html=True)
