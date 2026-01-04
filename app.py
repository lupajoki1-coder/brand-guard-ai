import streamlit as st
import google.generativeai as genai
import Levenshtein
from googlesearch import search
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="BrandGuard AI 2.5", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SIDEBAR & KEAMANAN API ---
with st.sidebar:
    st.header("⚙️ Konfigurasi Sistem")
    
    # LOGIKA KEAMANAN: Cek Secrets dulu
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Terdeteksi (Auto)")
    else:
        api_key = st.text_input("Masukkan Gemini API Key", type="password")
        st.caption("Belum punya? [Dapatkan disini](https://aistudio.google.com/app/apikey)")

    st.divider()
    
    # PILIH MODEL (Update 2026)
    st.subheader("🧠 Model Engine")
    selected_model = st.selectbox(
        "Versi Model:",
        (
            "gemini-2.5-flash",      # REKOMENDASI: Stabil & Cepat
            "gemini-2.0-flash-exp",  # Alternatif Experimental
            "gemini-1.5-pro"         # Alternatif High-Reasoning
        ),
        index=0
    )
    
    st.info(f"Status: Menggunakan **{selected_model}**")

# --- 3. FUNGSI PENCARIAN (GOOGLE DORKING) ---
def search_pdki_dynamic(brand_name):
    """Mencari jejak merek di situs PDKI via Google Search Index"""
    competitors = []
    query = f'site:pdki-indonesia.dgip.go.id "{brand_name}"'
    
    try:
        # Mengambil maksimal 10 hasil
        for url in search(query, num_results=10, lang="id"):
            competitors.append(url)
    except Exception as e:
        st.warning(f"Google Search Warning: {e}")
    
    return competitors

# --- 4. FUNGSI ANALISIS AI ---
def analyze_brand_ai(key, model_ver, brand, cls, competitors):
    if not key: return "⚠️ Error: API Key tidak ditemukan."
    
    genai.configure(api_key=key)
    
    # Konfigurasi Model dengan Error Handling
    try:
        model = genai.GenerativeModel(model_ver)
    except Exception as e:
        return f"Error Inisialisasi Model: {e}"

    # Siapkan Data
    comp_str = "\n".join(competitors) if competitors else "Tidak ditemukan link spesifik di index pencarian."
    
    # Prompt (Instruksi) untuk AI
    prompt = f"""
    Bertindaklah sebagai Konsultan HKI (Hak Kekayaan Intelektual) Profesional.
    
    DATA ANALISIS:
    - Nama Merek: "{brand}"
    - Kelas: {cls}
    - Temuan Index PDKI: 
    {comp_str}
    
    TUGAS ANDA:
    Lakukan analisis risiko berdasarkan UU Merek No 20 Tahun 2016.
    1. **Cek Fonetik/Bunyi**: Apakah nama ini mirip dengan merek terkenal atau temuan link di atas?
    2. **Cek Semantik**: Apakah nama ini melanggar norma, agama, atau terlalu umum (deskriptif)?
    3. **Kesimpulan**: Berikan persentase peluang keberhasilan (0-100%) dan saran singkat.
    
    Jawab dengan format Markdown yang rapi.
    """
    
    with st.spinner(f'⚡ {model_ver} sedang menganalisis hukum...'):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Terjadi kesalahan API: {e}. \nSaran: Coba ganti model ke versi lain di sidebar."

# --- 5. ANTARMUKA UTAMA (UI) ---
st.title("⚡ BrandGuard AI: Forensic")
st.markdown("Sistem analisis kelayakan merek berbasis AI Generatif dan Data Index Web.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📝 Input Data")
    brand_name = st.text_input("Nama Merek", "MANAKALA")
    brand_class = st.selectbox("Kelas Merek", 
                               ["Kelas 3 (Kosmetik/Parfum)", 
                                "Kelas 25 (Pakaian)", 
                                "Kelas 30 (Makanan/Kopi)", 
                                "Kelas 35 (Jasa Toko)", 
                                "Lainnya"])
    
    analyze_btn = st.button("🔍 Mulai Investigasi", type="primary", use_container_width=True)

with col2:
    if analyze_btn:
        if not api_key:
            st.error("⚠️ API Key belum diisi! Masukkan di sidebar atau set di Secrets.")
        else:
            # Tahap A: Cari Bukti
            st.success(f"Memproses merek: **{brand_name}**")
            
            with st.expander("📂 Bukti Digital (Temuan Index Web)", expanded=False):
                found_links = search_pdki_dynamic(brand_name)
                if found_links:
                    for link in found_links:
                        st.markdown(f"- [{link}]({link})")
                else:
                    st.info("Belum ditemukan data spesifik di index Google (Indikasi awal yang baik).")

            # Tahap B: Analisis AI
            result = analyze_brand_ai(api_key, selected_model, brand_name, brand_class, found_links)
            
            st.divider()
            st.subheader("📊 Hasil Analisis Forensik")
            st.markdown(result)
