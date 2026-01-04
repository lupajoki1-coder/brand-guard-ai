import streamlit as st
import google.generativeai as genai
import Levenshtein
from googlesearch import search

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="BrandGuard AI 2.5", page_icon="⚡", layout="wide")

# --- JUDUL & SIDEBAR ---
st.title("⚡ BrandGuard AI: Forensic 2.5")
st.markdown("""
Aplikasi Forensik Merek bertenaga **Google Gemini 2.5 Flash**.
Model terbaru ini memiliki latensi ultra-rendah dan penalaran multimodal yang lebih tajam.
""")

with st.sidebar:
    st.header("⚙️ Konfigurasi Sistem")
    api_key = st.text_input("Masukkan Google Gemini API Key", type="password")
    st.markdown("[Dapatkan API Key Gratis di Google AI Studio](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    st.subheader("🧠 Model Engine")
    # Selector Model (Diupdate untuk Tahun 2026)
    selected_model = st.selectbox(
        "Versi Model Aktif:",
        (
            "gemini-2.5-flash",      # ✅ REKOMENDASI UTAMA (Stable 2026)
            "gemini-2.5-pro",        # Opsi High-Intelligence
            "gemini-2.0-flash"       # Legacy Fallback (Expire Soon)
        ),
        index=0
    )
    
    st.info(f"Menggunakan Engine: **{selected_model}**")
    if "2.5" in selected_model:
        st.caption("🚀 Status: Latest Stable Build (Jan 2026)")

# --- FUNGSI 1: DINAMIS SEARCH PDKI (GOOGLE DORKING) ---
def search_pdki_dynamic(brand_name):
    """
    Mencari jejak merek di situs PDKI menggunakan Google Search Index.
    """
    competitors = []
    # Query spesifik ke database DJKI
    query = f'site:pdki-indonesia.dgip.go.id "{brand_name}"'
    
    try:
        # Mengambil 10 hasil teratas
        for url in search(query, num_results=10, lang="id"):
            competitors.append(url)
    except Exception as e:
        st.warning(f"Akses pencarian terbatas: {e}")
    
    return competitors

# --- FUNGSI 2: ANALISIS GEMINI 2.5 FLASH ---
def analyze_brand_ai(api_key, model_version, brand, cls, competitors):
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel(model_version)
    except Exception as e:
        return f"Error Model: {e}. Pastikan API Key Anda memiliki akses ke model 2.5."
    
    comp_str = "\n".join(competitors) if competitors else "Tidak ditemukan link spesifik di index pencarian Google."
    
    # Prompt yang dioptimalkan untuk Gemini 2.5
    prompt = f"""
    Bertindaklah sebagai Konsultan HKI Senior di Indonesia.
    
    OBJEK: Merek "{brand}" (Kelas {cls})
    TEMUAN INDEX: {comp_str}
    
    Lakukan 'Reasoning Trace' singkat, lalu berikan kesimpulan:
    1. **Analisis Fonetik & Visual**: Apakah ada kemiripan bunyi/tampilan dengan merek terkenal atau temuan di atas?
    2. **Analisis Semantik**: Apakah kata ini melanggar ketertiban umum/agama (Pasal 20 UU Merek)?
    3. **Skor Keberhasilan**: (0-100%).
    
    Jawab tegas, padat, dan gunakan format Markdown.
    """
    
    with st.spinner(f'⚡ Gemini {model_version} sedang memproses data...'):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Gagal memproses: {e}. \nCoba ganti ke 'gemini-2.0-flash' jika akun Anda belum migrasi penuh."

# --- ANTARMUKA UTAMA ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Input Data Merek")
    brand_name = st.text_input("Nama Merek", "MANAKALA")
    brand_class = st.selectbox("Kelas Merek", 
                               ["Kelas 3 (Kosmetik/Parfum)", 
                                "Kelas 9 (Teknologi)",
                                "Kelas 25 (Pakaian)", 
                                "Kelas 30 (Kopi/Makanan)", 
                                "Kelas 35 (Jasa)",
                                "Lainnya"])
    
    start_btn = st.button("🔍 Mulai Investigasi", type="primary")

with col2:
    if start_btn:
        if not api_key:
            st.error("⚠️ Masukkan API Key terlebih dahulu.")
        else:
            # Tahap 1: Bukti Digital
            st.success(f"Menginvestigasi: **{brand_name}**")
            
            with st.expander("📂 Bukti Digital (Index PDKI)"):
                found_links = search_pdki_dynamic(brand_name)
                if found_links:
                    for link in found_links:
                        st.markdown(f"- [{link}]({link})")
                else:
                    st.write("Belum ditemukan index spesifik. (Indikasi Positif)")

            # Tahap 2: AI Analysis
            analysis_result = analyze_brand_ai(api_key, selected_model, brand_name, brand_class, found_links)
            
            st.markdown("---")
            st.subheader("📊 Laporan Forensik (Gemini 2.5)")
            st.markdown(analysis_result)