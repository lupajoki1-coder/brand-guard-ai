import streamlit as st
import google.generativeai as genai
from googlesearch import search
from fpdf import FPDF
from PIL import Image
import datetime

# --- 1. SYSTEM CONFIGURATION & CORPORATE UI ---
st.set_page_config(
    page_title="KSB Global Audit", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS: Corporate Auditor Aesthetic (Cold & Precise)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #f1f5f9; /* Slate-100 */
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Styling: Strict Borders */
    .audit-panel {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px; /* Boxy look for professional feel */
        padding: 25px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Headers */
    h1 { color: #0f172a; font-weight: 900; letter-spacing: -0.5px; text-transform: uppercase; font-size: 1.8rem; }
    h2 { color: #334155; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 2px solid #0f172a; padding-bottom: 10px; margin-bottom: 20px; }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 4px;
        border: 1px solid #94a3b8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Executive Button */
    .stButton>button {
        background-color: #0f172a; /* Slate-900 */
        color: white;
        border-radius: 4px;
        padding: 1rem 2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1e293b;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    
    /* Progress Bar Color */
    .stProgress > div > div > div > div {
        background-color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL REFERENCE DATA ---
NICE_CLASSES = [
    "CL 01 - Chemicals", "CL 02 - Paints", "CL 03 - Cosmetics & Cleaning", "CL 04 - Industrial Oils",
    "CL 05 - Pharmaceuticals", "CL 06 - Common Metals", "CL 07 - Machines", "CL 08 - Hand Tools",
    "CL 09 - Computer, Software, Electronics", "CL 10 - Medical Devices", "CL 11 - Lighting/Heating",
    "CL 12 - Vehicles", "CL 13 - Firearms", "CL 14 - Jewellery", "CL 15 - Musical Instruments",
    "CL 16 - Paper & Printed Matter", "CL 17 - Rubber Goods", "CL 18 - Leather Goods",
    "CL 19 - Building Materials", "CL 20 - Furniture", "CL 21 - Household Utensils",
    "CL 22 - Ropes & Textiles", "CL 23 - Yarns", "CL 24 - Textiles", "CL 25 - Clothing & Footwear",
    "CL 26 - Lace & Embroidery", "CL 27 - Carpets", "CL 28 - Games & Sporting Goods",
    "CL 29 - Meat, Fish, Poultry", "CL 30 - Coffee, Tea, Bread", "CL 31 - Agricultural",
    "CL 32 - Beers & Non-Alcoholic", "CL 33 - Alcoholic Beverages", "CL 34 - Tobacco",
    "CL 35 - Advertising & Business", "CL 36 - Insurance & Finance", "CL 37 - Construction",
    "CL 38 - Telecoms", "CL 39 - Transport", "CL 40 - Material Treatment",
    "CL 41 - Education & Entertainment", "CL 42 - Scientific & Tech Services",
    "CL 43 - Food & Drink Services", "CL 44 - Medical Services", "CL 45 - Legal & Security"
]

# --- 3. INTELLIGENCE ENGINE (SEARCH) ---
def global_index_search(keyword):
    """
    Melacak jejak merek di database:
    1. PDKI (Indonesia)
    2. WIPO (Global Brand Database)
    3. USPTO (US Trademark)
    Menggunakan teknik Dorking presisi.
    """
    results = []
    # Query Smart: Mencari di 3 database otoritas sekaligus
    query = f'("{keyword}") AND (site:pdki-indonesia.dgip.go.id OR site:branddb.wipo.int OR site:tmsearch.uspto.gov)'
    
    try:
        # Mengambil 10 hasil teratas untuk konteks global
        for url in search(query, num_results=10, lang="id"):
            results.append(url)
    except:
        pass
    return results

# --- 4. AUDIT CORE (GEMINI PROMPT ENGINEERING) ---
def execute_forensic_audit(api_key, brand, cls, competitors, image_file=None):
    genai.configure(api_key=api_key)
    # Menggunakan model multimodal terbaik saat ini
    model = genai.GenerativeModel("gemini-2.0-flash-exp") 
    
    comp_data = "\n".join(competitors) if competitors else "No direct identical matches found in public index."
    
    # PROMPT: STRICT AUDITOR PERSONA
    # Instruksi ini melarang "AI-speak" dan memaksa output teknis hukum.
    prompt = f"""
    ROLE: Chief Trademark Forensic Auditor.
    OBJECTIVE: Conduct a Section 2(d) Likelihood of Confusion analysis & Global distinctiveness check.
    
    CASE FILE:
    - Subject Mark: "{brand}"
    - Nice Class: {cls}
    - Visual Evidence: {"[LOGO ATTACHED]" if image_file else "[TEXT ONLY]"}
    - Database Index Traces: 
    {comp_data}
    
    AUDIT PROTOCOLS:
    1. PHONETIC: Analyze sound-alike risks against global brands (e.g., SANSUNG vs SAMSUNG).
    2. VISUAL: Analyze logo geometry/composition (if image provided) or word-shape.
    3. CONCEPTUAL: Check for translations/meanings in major languages (English/Indonesian) that might conflict.
    4. DISTINCTIVENESS: Is the term Generic or Descriptive? (e.g. "APPLE" for fruit is generic, "APPLE" for tech is distinct).

    OUTPUT REQUIREMENTS:
    - Tone: Clinical, Legal, Direct.
    - NO conversational fillers (No "Here is the result", No "I think").
    - Format: Strict Markdown Table.
    
    [REPORT STRUCTURE]
    
    ### 1. AUDIT SUMMARY
    (One concise paragraph stating the final verdict: APPROVED or REJECTED HIGH RISK).

    ### 2. FORENSIC MATRIX
    | PARAMETER | CRITICAL FINDINGS | RISK LEVEL |
    | :--- | :--- | :--- |
    | **Phonetic** | [Technical analysis of syllables/sound] | [HIGH/MED/LOW] |
    | **Visual** | [Analysis of design/shape/font] | [HIGH/MED/LOW] |
    | **Conceptual** | [Meaning/Translation analysis] | [HIGH/MED/LOW] |
    | **Global Trace** | [Reference to database findings] | [HIGH/MED/LOW] |

    ### 3. TACTICAL RECOMMENDATION
    - [Specific Actionable Advice 1]
    - [Specific Actionable Advice 2]
    
    FINAL RISK SCORE: [0-100]%
    """
    
    inputs = [prompt]
    if image_file:
        img = Image.open(image_file)
        inputs.append(img)
    
    try:
        response = model.generate_content(inputs)
        return response.text
    except Exception as e:
        return f"AUDIT FAILURE: {str(e)}"

# --- 5. PDF GENERATOR (GRID SYSTEM) ---
class CorporatePDF(FPDF):
    def header(self):
        # Professional Header
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'KSB GLOBAL FORENSIC REPORT', 0, 1, 'L')
        self.set_line_width(0.5)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Confidential Audit Doc | {datetime.date.today()}', 0, 0, 'R')

def generate_pdf(brand, cls, content, risk):
    pdf = CorporatePDF()
    pdf.add_page()
    
    # Case Meta
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 8, "SUBJECT MARK:", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(150, 8, f" {brand.upper()}", 1, 1, 'L', 0)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "CLASS:", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(150, 8, f" {cls}", 1, 1, 'L', 0)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "RISK STATUS:", 1, 0, 'L', 1)
    
    # Conditional Color for Risk
    if "HIGH" in risk: pdf.set_text_color(200, 0, 0)
    else: pdf.set_text_color(0, 100, 0)
    
    pdf.cell(150, 8, f" {risk}", 1, 1, 'L', 0)
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.ln(10)
    
    # Content Body
    pdf.set_font("Courier", "", 9) # Monospace for data precision look
    
    # Clean Markdown for PDF
    clean_content = content.encode('latin-1', 'replace').decode('latin-1')
    clean_content = clean_content.replace("**", "").replace("###", "").replace("|", " ")
    
    pdf.multi_cell(0, 5, clean_content)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 6. MAIN APPLICATION INTERFACE ---

# Header
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0f172a; padding-bottom: 10px; margin-bottom: 30px;">
    <div>
        <h1 style="margin:0; font-size: 24px;">KSB GLOBAL <span style="color:#64748b;">AUDIT</span></h1>
        <p style="margin:0; font-size: 12px; font-weight: 600; color: #64748b;">INTEGRATED TRADEMARK INTELLIGENCE SYSTEM</p>
    </div>
    <div style="background:#0f172a; color:white; padding:5px 10px; font-size:10px; font-weight:bold; letter-spacing:1px;">V.7.0 GLOBAL</div>
</div>
""", unsafe_allow_html=True)

# API Key Check
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("SYSTEM ERROR: API Credentials Missing. Check Secrets Configuration.")
    st.stop()

# MAIN FORM
with st.container():
    st.markdown('<div class="audit-panel">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1.5], gap="large")
    
    with c1:
        st.markdown("## 1. CASE DETAILS")
        brand_input = st.text_input("Trademark Subject", placeholder="ENTER MARK NAME")
        class_input = st.selectbox("Nice Classification", NICE_CLASSES)
        
    with c2:
        st.markdown("## 2. VISUAL EVIDENCE")
        img_input = st.file_uploader("Upload Logo/Specimen (Optional)", type=['png', 'jpg', 'jpeg'])
        if img_input:
            st.caption("EVIDENCE ATTACHED: YES")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # EXECUTE
    if st.button("INITIATE GLOBAL FORENSIC AUDIT"):
        if not brand_input:
            st.warning("INPUT REQUIRED: Trademark Subject Cannot Be Empty.")
        else:
            # UI State: Running
            status_box = st.empty()
            prog_bar = st.progress(0)
            
            # Phase 1: Global Search
            status_box.markdown("**PHASE 1: SCANNING GLOBAL INDEX (WIPO / USPTO / PDKI)...**")
            prog_bar.progress(25)
            
            # Melakukan pencarian cerdas ke 3 database via Google
            global_traces = global_index_search(brand_input)
            
            # Phase 2: AI Audit
            status_box.markdown("**PHASE 2: EXECUTING FORENSIC ALGORITHMS (PHONETIC/VISUAL)...**")
            prog_bar.progress(60)
            
            audit_report = execute_forensic_audit(api_key, brand_input, class_input, global_traces, img_input)
            
            prog_bar.progress(100)
            status_box.empty()
            prog_bar.empty()
            
            # OUTPUT DISPLAY
            st.markdown('<div class="audit-panel" style="border-left: 6px solid #0f172a;">', unsafe_allow_html=True)
            st.markdown("## AUDIT FINDINGS")
            
            # Render Markdown result
            st.markdown(audit_report)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # PDF EXPORT
            risk_det = "HIGH RISK" if "HIGH" in audit_report else "LOW/MEDIUM RISK"
            pdf_bytes = generate_pdf(brand_input, class_input, audit_report, risk_det)
            
            col_ex1, col_ex2 = st.columns([3, 1])
            with col_ex2:
                st.download_button(
                    label="📄 EXPORT OFFICIAL PDF",
                    data=pdf_bytes,
                    file_name=f"AUDIT_{brand_input.upper()}_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
