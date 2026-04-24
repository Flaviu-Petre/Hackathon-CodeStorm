import os
import json
import base64
import fitz  # PyMuPDF
from fpdf import FPDF
from groq import Groq
from dotenv import load_dotenv

# --- 1. CONFIGURARE ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Eroare: Nu am găsit GROQ_API_KEY în fișierul .env!")

client = Groq(api_key=GROQ_API_KEY)

INPUT_PDF = "plan_invatamant.pdf"  
OUTPUT_TEXT_PDF = "rezultat_final.pdf"
OUTPUT_JSON = "date_extrase_pentru_template.json"

# --- 2. FUNCȚII PENTRU AGENTUL 1 (OCR / VISION) ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def extract_text_with_vision_agent(image_bytes):
    """Agentul 1: Extrage textul brut din imagini (OCR)."""
    base64_image = encode_image(image_bytes)
    
    prompt = """
    Extract all the text from this image. 
    Return ONLY the extracted text, without any other comments, formatting, or introductions.
    Keep the Romanian diacritics (ă, â, î, ș, ț) exactly as they appear in the image.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    return chat_completion.choices[0].message.content

# --- 3. FUNCȚII PENTRU AGENTUL 2 (DATA EXTRACTOR) ---
def extract_json_with_logic_agent(full_extracted_text):
    """Agentul 2: Analizează textul și extrage datele într-un format JSON detaliat."""
    
    model_name = "llama-3.3-70b-versatile"
    
    system_prompt = """
    You are an advanced university administrative assistant. Your task is to extract complex information 
    from a raw 'Curriculum' document (OCR output) to populate databases and templates.
    
    You must return EXCLUSIVELY a valid JSON file, using EXACTLY the following structure:
    {
      "Date_despre_program": {
        "Institutia_de_invatamant_superior": "",
        "Facultatea": "",
        "Domeniul_de_studii": "",
        "Ciclul_de_studii": "",
        "Programul_de_studiu_Calificarea": ""
      },
      "Legenda_si_Observatii": {
        "Legenda": {
          "C1": "criteriul obligativității",
          "DI": "disciplină impusă (obligatorie)",
          "DO": "disciplină opțională (la alegere)"
          // ... extract ALL other abbreviations from the "Legenda" list and map them here.
        },
        "Observatii": [
          "text of the first observation (e.g., AI = nr. de ore de curs...)",
          "text of the second observation"
          // ... extract ALL other observations.
        ]
      },
      "Competente_profesionale": [
        {
          "Competenta": "text of the competence (e.g., CP1. Creează softuri...)",
          "Rezultate_invatare": [
            "text of the first associated learning outcome (e.g., RÎ 1.1. Absolventul...)"
          ]
        }
      ],
      "Competente_transversale": [
        {
          "Competenta": "text of the competence (e.g., CT1. Aplică competențe de bază...)",
          "Rezultate_invatare": [
            "text of the first associated learning outcome (e.g., RÎ 1.1. Absolventul...)"
          ]
        }
      ],
      "Discipline": [
        {
          "Denumirea_disciplinei": "",
          "C1_Obligativitate": "e.g., DI, DO, DFc",
          "C2_Continut": "e.g., DF, DS, DC",
          "Cod_disciplina": "e.g., AP001-ID",
          "Anul_de_studiu": "e.g., I, II or III",
          "Semestrul": "I or II",
          "Ore_AI": "number of hours from the AI column",
          "Ore_AT": "number of hours from the AT column",
          "Ore_TC": "number of hours from the TC column",
          "Ore_AA": "number of hours from the AA column",
          "Ore_SI": "number of hours from the SI column",
          "Forma_de_verificare_FV": "e.g., E, C, A/R",
          "Numarul_de_credite_Cr": "number of credits"
        }
      ]
    }
    
    CRITICAL Rules: 
    1. Legend and Observations Section: Locate chapter "6. DISCIPLINELE ȘI ACTIVITĂȚILE DIDACTICE ALOCATE PE ANI DE STUDII". Create the "Legenda" dictionary by mapping each abbreviation to its explanation (e.g., "Cr.": "nr. de credite"). Then, extract the paragraphs under the "Observații:" section and put them as strings in the "Observatii" array.
    2. Competence Sections: Extract both 'Competențe profesionale' (CPs) and 'Competențe transversale' (CTs). Group the Learning Outcomes (RÎ) under the specific Competence they belong to.
    3. Discipline Tables: Notice that tables have columns divided into Semester I and Semester II. A subject has its hours filled in only one of the semesters. Identify which semester contains the hours and write "I" or "II" in the "Semestrul" key, then extract the values (AI, AT, TC, AA, SI, FV, Cr) from that specific block.
    4. Extract ALL subjects and do not miss the C1, C2, and Discipline Code columns.
    5. If a cell is empty or information is missing in the document, leave the value as an empty string "".
    6. DO NOT add markdown (like ```json), introductions, or explanations. Return ONLY the raw JSON object.
    """

    print("\n🧠 Agentul 2 analizează textul brut și construiește JSON-ul detaliat...")
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the full text extracted from the PDF:\n\n{full_extracted_text}"}
        ],
        model=model_name,
        response_format={"type": "json_object"}, 
        temperature=0.1 
    )
    
    return chat_completion.choices[0].message.content


# --- 4. FLUXUL PRINCIPAL (ORCHESTRAREA) ---
def main():
    doc = fitz.open(INPUT_PDF)
    pdf_output = FPDF()
    pdf_output.set_auto_page_break(auto=True, margin=15)
    pdf_output.add_font("Arial", "", "arial.ttf")
    
    full_document_text = ""
    
    print(f"📄 Începe procesarea PDF-ului: {INPUT_PDF} ({len(doc)} pagini)")

    for page_num in range(len(doc)):
        print(f"👁️ Agentul Vision procesează pagina {page_num + 1}...")
        
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_bytes = pix.tobytes("jpeg")
        
        try:
            page_text = extract_text_with_vision_agent(image_bytes)
            full_document_text += f"\n--- Pagina {page_num + 1} ---\n{page_text}"
            
            pdf_output.add_page()
            pdf_output.set_font("Arial", size=11)
            pdf_output.multi_cell(0, 10, text=page_text)
            
        except Exception as e:
            print(f"❌ Eroare la pagina {page_num + 1}: {e}")

    pdf_output.output(OUTPUT_TEXT_PDF)
    print(f"\n✅ PAS 1 COMPLET: PDF-ul cu text a fost salvat ca: {OUTPUT_TEXT_PDF}")

    if full_document_text.strip():
        try:
            json_data = extract_json_with_logic_agent(full_document_text)
            
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                parsed_json = json.loads(json_data)
                json.dump(parsed_json, f, ensure_ascii=False, indent=4)
                
            print(f"✅ PAS 2 COMPLET: Datele structurate detaliat au fost salvate în: {OUTPUT_JSON}")
            
        except Exception as e:
            print(f"❌ Eroare la generarea JSON-ului: {e}")
    else:
        print("⚠️ Nu s-a putut extrage text din PDF, pasul JSON a fost anulat.")

if __name__ == "__main__":
    main()