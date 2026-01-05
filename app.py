import streamlit as st
import google.generativeai as genai
from googlesearch import search
from fpdf import FPDF
from PIL import Image
import io
import datetime

# --- 1. KONFIGURASI UI/UX PRO (MOBILE FRIENDLY & DEPTH) ---
st.set_page_config(
    page_title="KSB Suite: Forensic Audit", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Injection: Deep Glassmorphism & Responsive Fixes
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=Outfit:wght@400;700&display=swap');
    
    /* Background & Base */
    .stApp {
        background-color: #e2e8f0;
        background-image: 
            radial-gradient(at 0% 0%, hsla(210, 100%, 96%, 1) 0, transparent 50%), 
            radial-gradient(at 100% 100%, hsla(220, 100%, 94%, 1) 0, transparent 50%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* DEPTH EFFECT CARD (Glassmorphism) */
    .depth-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 
            0 10px 40px -10px rgba(0,0,0,0.1),
            0 0 0 1px rgba(255,255,255,0.5) inset; /* Inner glow */
        margin-bottom: 24px;
        transition: transform 0.3s ease;
    }
    
    /* Responsive Typography */
    h1 { font-family: 'Outfit', sans-serif; color: #0f172a; font-weight: 800; letter-spacing: -1px; }
    h2, h3 { font-family: 'Outfit', sans-serif; color: #1e293b; font-weight: 700; }
    p { color: #475569; line-height: 1.6; }
    
    /* Custom Inputs (More Depth) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) inset;
    }
    
    /* Primary Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.3);
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px -5px rgba(15, 23, 42, 0.4);
    }

    /* Fix Mobile Padding */
    @media (max-width: 640px) {
        .depth-card { padding: 20px; border-radius: 20px; }
        h1 { font-size: 1.8rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA REFERENSI: NICE CLASSIFICATION (VERBATIM LENGKAP) ---
# Mengacu pada standar Klasifikasi Nice yang legal dan resmi.
FULL_CLASSES = [
    "Kelas 1: Bahan Kimia (Industri, Sains, Fotografi)",
    "Kelas 2: Cat, Pernis, Pengawet Kayu",
    "Kelas 3: Kosmetik, Pembersih, Parfum, Skincare",
    "Kelas 4: Minyak Industri, Pelumas, Bahan Bakar",
    "Kelas 5: Farmasi, Obat, Suplemen, Makanan Bayi",
    "Kelas 6: Logam Tidak Mulia, Bahan Bangunan Logam",
    "Kelas 7: Mesin, Perkakas Mekanis, Motor",
    "Kelas 8: Perkakas Tangan (Manual), Pisau, Garpu",
    "Kelas 9: Alat Ilmiah, Software, Kacamata, Elektronik",
    "Kelas 10: Alat Bedah, Medis, Kedokteran Gigi",
    "Kelas 11: Alat Penerangan, Pemanas, Pendingin",
    "Kelas 12: Kendaraan, Alat Transportasi Darat/Air/Udara",
    "Kelas 13: Senjata Api, Amunisi, Kembang Api",
    "Kelas 14: Logam Mulia, Perhiasan, Jam Tangan",
    "Kelas 15: Alat Musik",
    "Kelas 16: Kertas, Karton, Alat Tulis, Cetakan",
    "Kelas 17: Karet, Plastik (Setengah Jadi), Pipa Fleksibel",
    "Kelas 18: Kulit, Tas, Dompet, Payung",
    "Kelas 19: Bahan Bangunan (Bukan Logam), Aspal",
    "Kelas 20: Perabot, Mebel, Cermin, Bingkai",
    "Kelas 21: Alat Rumah Tangga, Dapur, Gelas, Porselen",
    "Kelas 22: Tali, Jaring, Tenda, Karung",
    "Kelas 23: Benang dan Tali untuk Tekstil",
    "Kelas 24: Tekstil, Kain, Sprei, Selimut",
    "Kelas 25: Pakaian, Alas Kaki, Tutup Kepala",
    "Kelas 26: Renda, Bordir, Pita, Kancing",
    "Kelas 27: Karpet, Tikar, Linoleum",
    "Kelas 28: Mainan, Alat Olahraga, Game",
    "Kelas 29: Daging, Ikan, Unggas, Buah/Sayur Olahan",
    "Kelas 30: Kopi, Teh, Roti, Beras, Gula, Rempah",
    "Kelas 31: Hasil Pertanian Segar, Buah/Sayur Hidup",
    "Kelas 32: Bir, Minuman Non-Alkohol, Jus, Air Mineral",
    "Kelas 33: Minuman Beralkohol (Kecuali Bir)",
    "Kelas 34: Tembakau, Rokok, Korek Api",
    "Kelas 35: Periklanan, Manajemen Usaha, Toko (Retail)",
    "Kelas 36: Asuransi, Keuangan, Real Estate",
    "Kelas 37: Konstruksi, Perbaikan, Pemasangan",
    "Kelas 38: Telekomunikasi",
    "Kelas 39: Transportasi, Pengemasan, Wisata",
    "Kelas 40: Pengolahan Material (Jasa)",
    "Kelas 41: Pendidikan, Pelatihan, Hiburan, Olahraga",
    "Kelas 42: Jasa Ilmiah, Teknologi, Desain, IT",
    "Kelas 43: Jasa Penyediaan Makanan/Minuman (Resto/Kafe)",
    "Kelas 44: Jasa Medis, Kedokteran Hewan, Kecantikan",
    "Kelas 45: Jasa Hukum, Keamanan, Personal"
]

# --- 3. FUNGSI LOGIC (SEARCH & PDF) ---

def smart_pdki_search(keyword):
    """
    Rekomendasi Terbaik: Google Dorking Spesifik ke Server PDKI.
    Metode ini legal, tidak membebani server pemerintah, dan akurat.
    """
    results = []
    # Strategi: Cari "Nama" ATAU "Kata Kunci" di dalam situs PDKI
    query = f'site:pdki-indonesia.dgip.go.id "{keyword}" OR {keyword}'
    try:
        # Mengambil 8 hasil teratas untuk konteks
        for url in search(query, num_results=8, lang="id"):
            results.append(url)
    except:
        pass # Fail gracefully
    return results

def generate_pdf_report(brand, cls, analysis_text, risk):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header Professional
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(15, 23, 42) # Slate-900
    pdf.cell(0, 10, "AUDIT FORENSIK MEREK (KSB SUITE)", 0, 1, 'C')
    
    # Metadata Box
    pdf.set_fill_color(240, 249, 255) # Sky-50
    pdf.rect(10, 25, 190, 20, 'F')
    pdf.set_y(28)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"TARGET: {brand.upper()}", 0, 1, 'C')
    pdf.cell(0, 5, f"KELAS: {cls[:40]}...", 0, 1, 'C')
    pdf.cell(0, 5, f"STATUS RISIKO: {risk}", 0, 1, 'C')
    pdf.ln(10)
    
    # Content Cleaning (Remove Markdown)
    pdf.set_font("Courier", "", 10)
    clean_txt = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    clean_txt = clean_txt.replace("*", "").replace("#", "").replace("|", " ")
    
    pdf.multi_cell(0, 6, clean_txt)
    
    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"Generated: {datetime.date.today()} | Confidential", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. ENGINE AI VERBATIM (GEMINI 2.5 FLASH) ---
def analyze_with_context(api_key, brand, cls, competitors, image_file=None):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash") # Multimodal Model
    
    comp_str = "\n".join(competitors) if competitors else "Tidak ditemukan data spesifik di index publik."
    
    # Prompt dibangun berdasarkan "Tips Merek.pdf" (Verbatim Knowledge)
    prompt_text = f"""
    ROLE: Auditor Merek Senior (DJKI Standar).
    TONE: Direct, Evidence-Based, No Fluff.
    
    AUDIT TARGET:
    - Merek: "{brand}"
    - Kelas: {cls}
    - Image Uploaded: {"YA" if image_file else "TIDAK"}
    
    DATABASE CONTEXT (PDKI Findings):
    {comp_str}

    INSTRUKSI AUDIT (BERDASARKAN UU MEREK NO 20/2016):
    Lakukan analisis mendalam menggunakan prinsip-prinsip berikut (Verbatim Reference):
    
    1. **FONETIK (TES TELINGA):** [Ref: Slide 3 PDF]
       - Apakah bunyinya mirip dengan merek terkenal? (Contoh kasus: SANSUNG vs SAMSUNG).
       - Hati-hati dengan "Si Kembar Beda Ejaan".
       
    2. **VISUAL (JIKA ADA GAMBAR):** [Ref: Slide 4 PDF]
       - Cek "Visual Similarity". Apakah logo memiliki bentuk geometris yang meniru merek lain?
       - Jika tidak ada gambar, analisis potensi visual teksnya.
       
    3. **KONSEPTUAL (MAKNA):** [Ref: Slide 5 PDF]
       - Cek terjemahan (Contoh: RED BULL vs BANTENG MERAH).
       - Cek makna spesifik dalam bahasa asing/daerah.
       
    4. **DISTINGSI (DAYA PEMBEDA):** [Ref: Slide 6 PDF]
       - Apakah nama ini DESKRIPTIF? (Contoh: "GULA MANIS" = Ditolak Mutlak).
       - Nama harus unik, bukan kata umum (Generik).

    OUTPUT FORMAT (TABEL MARKDOWN):
    Berikan satu tabel matriks risiko (Parameter | Temuan | Status).
    Diakhiri dengan SKOR PELUANG (0-100%) dan REKOMENDASI FINAL.
    """
    
    inputs = [prompt_text]
    if image_file:
        img = Image.open(image_file)
        inputs.append(img)
        inputs.append("Ini adalah logo visual yang diajukan untuk merek ini.")

    try:
        response = model.generate_content(inputs)
        return response.text
    except Exception as e:
        return f"Error Analisis: {str(e)}"

# --- 5. TAMPILAN APLIKASI UTAMA ---

# Header Depth Effect
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="margin:0;">KSB SUITE <span style="color:#64748b; font-size:0.5em; vertical-align:middle; border:1px solid #cbd5e1; border-radius:8px; padding:2px 8px;">FORENSIC</span></h1>
    <p style="font-size: 0.9em; font-weight: 600; color: #64748b; margin-top:5px;">AI-POWERED TRADEMARK INTELLIGENCE</p>
</div>
""", unsafe_allow_html=True)

# API Key Auto-Check
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.warning("⚠️ API Key tidak terdeteksi di Secrets.")
    api_key = st.text_input("Input Manual API Key", type="password")

# --- FORM INPUT (DALAM CARD) ---
with st.container():
    st.markdown('<div class="depth-card">', unsafe_allow_html=True)
    
    # Grid Layout untuk Input (Responsive)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 1. Identitas Merek")
        brand_name = st.text_input("Nama Merek", placeholder="Contoh: KASHAFA")
        brand_class = st.selectbox("Kelas Merek (Nice Classification)", FULL_CLASSES)
    
    with col2:
        st.markdown("### 2. Bukti Visual (Opsional)")
        uploaded_file = st.file_uploader("Upload Logo (JPG/PNG, Max 5MB)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, width=100, caption="Preview Logo")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Action Button
    run_btn = st.button("JALANKAN AUDIT FORENSIK ⚡")

# --- EKSEKUSI & HASIL ---
if run_btn:
    if not api_key or not brand_name:
        st.error("Mohon lengkapi Nama Merek dan pastikan API Key aktif.")
    else:
        # Progress UI
        progress_text = st.empty()
        bar = st.progress(0)
        
        # Step 1: Legal Search
        progress_text.text("🔍 Memindai Index PDKI (Legal Search)...")
        bar.progress(30)
        findings = smart_pdki_search(brand_name)
        
        # Step 2: AI Reasoning
        progress_text.text("🧠 Menganalisis Fonetik, Visual, & Konseptual...")
        bar.progress(70)
        
        analysis_result = analyze_with_context(api_key, brand_name, brand_class, findings, uploaded_file)
        
        bar.progress(100)
        bar.empty()
        progress_text.empty()
        
        # --- HASIL OUTPUT (DEPTH CARD) ---
        st.markdown(f"""
        <div class="depth-card" style="border-top: 5px solid #0f172a;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h2 style="margin:0;">HASIL AUDIT: {brand_name.upper()}</h2>
                <span style="background:#e2e8f0; padding:5px 10px; border-radius:8px; font-weight:bold; font-size:0.8em; color:#475569;">VERIFIED BY GEMINI 2.5</span>
            </div>
            {analysis_result.replace('<table>', '<table style="width:100%; border-collapse:collapse;">')} 
        </div>
        """, unsafe_allow_html=True)
        # Note: Replace logic above is simple fix to ensure table styling sticks in markdown
        
        # PDF Generator Logic
        risk_status = "HIGH" if "🔴" in analysis_result else "SAFE"
        pdf_bytes = generate_pdf_report(brand_name, brand_class, analysis_result, risk_status)
        
        col_d1, col_d2 = st.columns([3, 1])
        with col_d2:
            st.download_button(
                label="📥 DOWNLOAD REPORT (PDF)",
                data=pdf_bytes,
                file_name=f"AUDIT_{brand_name.upper()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# Footer
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
