import os
import json
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv

from calcule_matematice import calculeaza_date_materie 

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# CONFIGURARE FIȘIERE
PLAN_JSON = "date_extrase_pentru_template.json"
BIBLIO_JSON = "bibliografie_google_scholar_filtrata.json"
FISA_INPUT = "fisa_disciplina-21-24.pdf"

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def identify_subject(fisa_text, plan_data):
    """Pasul 1: Agentul identifică materia din planul de învățământ."""
    subjects_list = [
        {"Cod": d.get("Cod_disciplina"), "Nume": d.get("Denumirea_disciplinei")} 
        for d in plan_data.get("Discipline", [])
    ]
    
    discovery_prompt = f"""
    Based on the following syllabus text, identify which subject from the list below it refers to.
    Return ONLY the course code (Cod_disciplina).
    
    SYLLABUS TEXT START:
    {fisa_text[:2000]}
    
    SUBJECTS LIST:
    {json.dumps(subjects_list, ensure_ascii=False)}
    """
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": discovery_prompt}],
        model="qwen/qwen3-32b",
        temperature=0
    )
    return completion.choices[0].message.content.strip()

def run_compliance_audit(fisa_text, ground_truth):
    """Pasul 3: Agentul verifică neconcordanțele."""
    
    # PROMPT-UL PENTRU AGENT (Limba Engleză)
    system_prompt = """
    You are an Academic Compliance Auditor. Your task is to compare a Professor's Syllabus against the official "Ground Truth" data.
    
    You will be provided with:
    1. [GROUND TRUTH]: Calculated math values, official curriculum data, competencies, and recommended bibliography.
    2. [PROFESSOR SYLLABUS]: The text from the document submitted by the professor.

    YOUR MISSION:
    - Verify if the Syllabus values (Credits, Hours, Evaluation Type) match the Ground Truth.
    - Check if the math calculations in the syllabus (Individual study, total hours) match the Ground Truth calculations.
    - Check if the competencies mentioned in the syllabus match the official ones.
    - Verify if the bibliography is up to date based on the provided list.

    OUTPUT RULES:
    - Return a STRICT JSON object.
    - ALL explanations and findings must be in ROMANIAN.
    - If no discrepancies are found in a category, return an empty list [].
    """
    
    user_message = f"""
    [GROUND TRUTH DATA]:
    {json.dumps(ground_truth, indent=2, ensure_ascii=False)}
    
    [PROFESSOR SYLLABUS TEXT]:
    {fisa_text}
    """

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        model="qwen/qwen3-32b",
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return completion.choices[0].message.content

def main():
    # 1. Extragere text
    fisa_text = extract_text_from_pdf(FISA_INPUT)
    
    # 2. Încărcare Plan
    with open(PLAN_JSON, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    # 3. Identificare Dinamică
    cod_identificat = identify_subject(fisa_text, plan_data)
    print(f"🔍 Materia a fost identificată automat: {cod_identificat}")

    # 4. Generare Ground Truth (Matematică + Date Oficiale)
    math_results = calculeaza_date_materie(PLAN_JSON, cod_identificat)
    
    with open(BIBLIO_JSON, "r", encoding="utf-8") as f:
        biblio_full = json.load(f)
    
    materia_data = next((d for d in plan_data["Discipline"] if d["Cod_disciplina"] == cod_identificat), {})
    
    ground_truth = {
        "Math_Calculations": math_results,
        "Official_Curriculum": materia_data,
        "Official_Competencies": {
            "Prof": plan_data.get("Competente_profesionale", []),
            "Trans": plan_data.get("Competente_transversale", [])
        },
        "Recommended_Bibliography": biblio_full.get(materia_data.get("Denumirea_disciplinei"), [])
    }

    # 5. Audit AI
    report_json = run_compliance_audit(fisa_text, ground_truth)
    
    # 6. Salvare Rezultat
    with open("neconcordante_fisa.json", "w", encoding="utf-8") as f:
        json.dump(json.loads(report_json), f, ensure_ascii=False, indent=4)
    
    print("✅ Audit finalizat. Rezultatele sunt în 'neconcordante_fisa.json'.")

if __name__ == "__main__":
    main()