import os
import json
import fitz  # PyMuPDF
import re
from groq import Groq
from dotenv import load_dotenv

# Importăm noua metodă de procesare a întregului plan de învățământ
from calcule_matematice import proceseaza_toate_materiile 

# --- CONFIGURARE ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLAN_JSON = "date_extrase_pentru_template.json"
BIBLIO_JSON = "bibliografie_google_scholar_filtrata.json"
FISA_INPUT = "fisa_disciplina-21-24.pdf"
OUTPUT_AUDITAT = "fisa_disciplina_HIGHLIGHTED.pdf"

def extract_text_from_pdf(pdf_path):
    """Extrage textul brut din fișierul PDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def apply_highlights_to_pdf(pdf_path, highlights):
    """Căutăm fragmentele identificate de AI și aplicăm marcajele pe PDF."""
    doc = fitz.open(pdf_path)
    for item in highlights:
        target_text = item.get("text_exact")
        comment = item.get("comentariu")
        if not target_text: continue
        
        for page in doc:
            # Căutăm coordonatele textului exact în pagină
            text_instances = page.search_for(target_text)
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_info(content=comment, title="Eroare de Audit")
                annot.update()
    doc.save(OUTPUT_AUDITAT)
    return OUTPUT_AUDITAT

def identify_subject(fisa_text, plan_data):
    """Agentul identifică codul materiei folosind o logică de potrivire strictă."""
    discipline = plan_data.get("Discipline", [])
    subjects_list = [{"Cod": d.get("Cod_disciplina"), "Nume": d.get("Denumirea_disciplinei")} for d in discipline]
    
    prompt = f"""
    Analizează textul de mai jos și identifică CODUL DISCIPLINEI (de forma XX00-ID).
    Ignoră codurile administrative (ex: F03.1).
    Alege STRICT codul corespunzător din această listă:
    {json.dumps(subjects_list, ensure_ascii=False)}
    
    Răspunde DOAR cu codul (ex: IT14-ID).
    Text PDF: {fisa_text[:1500]}
    """
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0
    )
    
    res = completion.choices[0].message.content.strip()
    match = re.search(r'[A-Z]{2}\d{2}-ID', res)
    return match.group() if match else res

def run_visual_audit_agent(fisa_text, ground_truth):
    """Agentul compară fișa cu datele calculate și extrage fragmente UNICE pentru highlight."""
    str_truth = json.dumps(ground_truth, separators=(',', ':'), ensure_ascii=False)
    
    # Am adăugat explicit cuvântul JSON în prompt
    system_prompt = r"""
    You are a Strict PDF Annotation Assistant. Your goal is to find discrepancies between [GROUND TRUTH] and [SYLLABUS].
    
    CRITICAL RULES:
    1. Identify specific strings of text from the [SYLLABUS] that are wrong.
    2. THE "text_exact" MUST BE UNIQUE. NEVER return a single number (e.g., "4") or a single word. 
       You MUST include 3-5 surrounding words from the syllabus so the PDF search engine finds the EXACT spot.
    3. NO PEDAGOGICAL JUDGMENT. Only compare raw numbers and competencies.
    4. Provide a brief explanation in Romanian in 'comentariu'.

    You MUST return the response in a VALID JSON format using this SCHEMA:
    { "highlights": [ { "text_exact": "exact unique phrase from pdf", "comentariu": "explanation" } ] }
    """
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"[GROUND TRUTH]: {str_truth}\n\n[SYLLABUS]: {fisa_text[:8000]}"}
        ],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"}, # Aceasta forțează eroarea dacă prompt-ul nu conține "json"
        temperature=0.1
    )
    return json.loads(completion.choices[0].message.content)

def main():
    print("🧮 Pasul 1: Procesare date matematice...")
    proceseaza_toate_materiile(PLAN_JSON) 
    
    print("📄 Pasul 2: Extragere text PDF...")
    fisa_text = extract_text_from_pdf(FISA_INPUT)
    
    with open(PLAN_JSON, 'r', encoding='utf-8') as f:
        plan_data = json.load(f)

    print("🔍 Pasul 3: Identificare materie...")
    cod_identificat = identify_subject(fisa_text, plan_data)
    
    materia_oficiala = next((d for d in plan_data.get("Discipline", []) 
                           if d.get("Cod_disciplina") == cod_identificat), None)
    
    # Fallback pe nume dacă codul nu e valid
    if not materia_oficiala:
        print(f"⚠️ Codul '{cod_identificat}' nu e valid. Încercăm identificarea după nume...")
        for d in plan_data.get("Discipline", []):
            if d.get("Denumirea_disciplinei", "").lower() in fisa_text[:500].lower():
                materia_oficiala = d
                cod_identificat = d.get("Cod_disciplina")
                break

    if not materia_oficiala:
        print("❌ EROARE: Materia nu a putut fi identificată.")
        return

    print(f"✅ Materie identificată: {cod_identificat} ({materia_oficiala.get('Denumirea_disciplinei')})")

    # Pregătire Ground Truth pentru audit
    ground_truth = {
        "Credite": materia_oficiala.get("Numarul_de_credite_Cr"),
        "Total_Ore_Semestru": materia_oficiala.get("Total_ore_semestru"),
        "Ore_Studiu_Individual": materia_oficiala.get("Total_ore_studiu_individual"),
        "Ore_Didactice_Totale": materia_oficiala.get("Total_ore_didactice"),
        "Forma_Evaluare": materia_oficiala.get("Forma_de_verificare_FV"),
        "Competente_Oficiale": {
            "Profesionale": plan_data.get("Competente_profesionale", []),
            "Transversale": plan_data.get("Competente_transversale", [])
        }
    }

    print("🤖 Pasul 4: Analiză AI și localizare erori...")
    audit_results = run_visual_audit_agent(fisa_text, ground_truth)
    
    print("🖍️ Pasul 5: Aplicare highlight-uri pe PDF...")
    final_pdf = apply_highlights_to_pdf(FISA_INPUT, audit_results.get("highlights", []))
    
    print(f"✨ Audit finalizat! Fișier generat: {final_pdf}")

if __name__ == "__main__":
    main()