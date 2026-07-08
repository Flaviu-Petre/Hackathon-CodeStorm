# Hackathon CodeStorm: AI Syllabus Generator & Auditor

Acest proiect reprezintă o soluție digitală end-to-end, bazată pe Inteligență Artificială, creată pentru a sprijini cadrele didactice și departamentele administrative din universități. Sistemul automatizează complet procesul de extragere a datelor din planurile de învățământ, generarea fișelor de disciplină în format profesional (LaTeX) și auditarea inteligentă a fișelor deja existente pentru a identifica discrepanțele.

## Funcționalități principale

1. **Extragere inteligentă a aatelor (OCR & NLP):** Citirea planurilor de învățământ din format PDF și transformarea lor în date structurate (JSON) cu ajutorul modelelor Llama via Groq API.
2. **Calcul automatizat:** Procesarea și calcularea formulelor administrative (total ore pe semestru, ore de studiu individual, credite etc.) fără intervenție umană.
3. **Generare de documente LaTeX:** Crearea automată a fișelor de disciplină sub formă de documente `.tex` formatate.
4. **Validare date:** Verificarea a fișierelor `.tex` generate pentru a asigura că nicio informație din planul de învățământ nu s-a pierdut pe parcurs.
5. **Auditor Șef (AI Inspector):** Un modul dedicat care analizează o fișă de disciplină PDF existentă, o compară cu "Ground Truth-ul" (planul de învățământ) și **evidențiază direct pe PDF (Highlight)** neconcordanțele sau erorile de redactare.

---

## Arhitectura sistemului

Sistemul este împărțit în mai mulți agenți și scripturi modulare, orchestrate centralizat:

* `app_pipeline.py` - **Orchestratorul.** Rulează întregul flux de la A la Z într-o ordine strictă (Extragere -> Calcul -> Generare -> Validare).
* `Extractor_Text.py` - **Agentul de vizualizare și procesare.** Preia `plan_invatamant.pdf`, folosește Vision AI pentru OCR, iar apoi un Data Extractor AI (`llama-3.3-70b-versatile`) mapează textul brut într-un fișier strict structurat: `date_extrase_pentru_template.json`.
* `calcule_matematice.py` - **Modulul de logică matematică.** Preia JSON-ul extras și derivează restul câmpurilor necesare pentru fișa disciplinei (ex. calculul orelor didactice totale, studiul individual).
* `ScriptLatex.py` - **Generatorul de template.** Folosește Jinja2 pentru a injecta datele din JSON într-un template LaTeX, generând fișiere `.tex` individuale pentru fiecare materie în folderul `output/`.
* `validator.py` - **Modulul de asigurare a calității.** Citește fișierele LaTeX generate și confirmă că valorile textuale și numerice corespund exact cu cele din JSON-ul original.
* `Auditor_Sef.py` - **Agentul de auditare vizuală.** Funcționează independent pentru a găsi erori în fișe deja redactate (`fisa_disciplina-21-24.pdf`), returnând un document nou cu adnotări (`fisa_disciplina_HIGHLIGHTED.pdf`).

---

## Tehnologii utilizate

* **Limbaj:** Python 
* **AI / LLM:** Groq API (modelele `meta-llama/llama-4-scout-17b-16e-instruct` și `llama-3.3-70b-versatile`)
* **Procesare PDF:** PyMuPDF (`fitz`), FPDF2
* **Templating:** Jinja2
* **Tipografiere:** LaTeX
