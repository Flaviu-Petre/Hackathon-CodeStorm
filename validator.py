import json
import os

def escape_latex(text):
    """Aplică aceleași reguli de escape ca în scriptul de generare."""
    if not isinstance(text, str):
        return str(text)
    chars_to_escape = {'&': r'\&', '%': r'\%', '_': r'\_'}
    return "".join(chars_to_escape.get(c, c) for c in text)

def valideaza_fisier(filepath, json_data):
    # Citim conținutul fișierului LaTeX
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Eroare la citirea fișierului {filepath}: {e}")
        return

    filename = os.path.basename(filepath).replace(".tex", "")
    
    # Căutăm disciplina în JSON bazându-ne pe numele fișierului
    disc_data = None
    for d in json_data['Discipline']:
        # Replicăm logica de creare a numelui de fișier din main.py
        file_name_format = d['Denumirea_disciplinei'].replace(" ", "_")
        safe_name = "".join(c for c in file_name_format if c.isalnum() or c in ('_', '-'))
        
        if safe_name == filename:
            disc_data = d
            break

    if not disc_data:
        print(f"[!] AVERTISMENT: Nu am găsit corespondent în JSON pentru fișierul: {filename}.tex")
        return

    conflicte = []

    # 1. Verificare Date Program
    for key, val in json_data['Date_despre_program'].items():
        expected = escape_latex(val)
        if expected not in content:
            conflicte.append(f"Date Program: Lipsește sau este diferit '{expected}' (Câmp: {key})")

    # 2. Verificare Date Disciplină (Texte)
    texte_de_verificat = ['Denumirea_disciplinei', 'Anul_de_studiu', 'Semestrul', 'Forma_de_verificare_FV', 'C1_Obligativitate']
    for key in texte_de_verificat:
        expected = escape_latex(str(disc_data.get(key, "")))
        if expected not in content:
            conflicte.append(f"Date Disciplină: Lipsește valoarea '{expected}' pentru {key}")

    # 3. Verificare Calcule și Ore
    chei_ore = ['Ore_AI', 'Ore_AT', 'Ore_TC', 'Ore_AA', 'Ore_SI']
    ore_validate = {}
    for key in chei_ore:
        val = disc_data.get(key, "0")
        ore_validate[key] = int(val) if str(val).strip() else 0

    credite = disc_data.get('Numarul_de_credite_Cr', 0)
    
    # SCHIMBARE AICI: Luăm variabila care chiar e printată la punctul 3.4 în LaTeX
    total_plan_invatamant = disc_data.get('Total_ore_din_planul_de_invatamant', 0)
    total_semestru = disc_data.get('Total_ore_semestru', 0)
    total_individual = disc_data.get('Total_ore_studiu_individual', 0)

    # Căutăm numerele sub formă de string în documentul .tex
    numere_de_verificat = {
        "Număr de credite": credite,
        "Total ore din planul de invatamant": total_plan_invatamant,
        "Total ore pe semestru": total_semestru,
        "Total ore studiu individual": total_individual
    }

    for nume_camp, valoare in numere_de_verificat.items():
        if str(valoare) not in content:
            conflicte.append(f"Validare Date: Nu am găsit valoarea '{valoare}' (calculată de math.py) pentru {nume_camp}")

    # 4. Verificare Competențe (eșantion de text)
    # Verificăm dacă măcar primele 10 caractere dintr-o competență generată au ajuns în document
    if len(json_data.get('Competente_profesionale', [])) > 0:
        prima_comp_profesionala = json_data['Competente_profesionale'][0]['Competenta']
        esantion = escape_latex(prima_comp_profesionala[:10])
        if esantion not in content:
            conflicte.append("Competențe: Blocul de competențe profesionale pare să lipsească sau nu a fost mapat.")

    # Raportare finală
    if conflicte:
        print(f"[X] EȘEC: S-au găsit {len(conflicte)} conflicte în '{filename}.tex':")
        for c in conflicte:
            print(f"    - {c}")
        print("-" * 50)
    else:
        print(f"[V] SUCCES: Validare trecută fără probleme pentru '{filename}.tex'.")

def main():
    json_path = 'date_extrase_pentru_template.json'
    output_dir = 'output'

    if not os.path.exists(json_path):
        print(f"Eroare: Nu găsesc fișierul JSON la {json_path}")
        return

    if not os.path.exists(output_dir):
        print(f"Eroare: Nu găsesc folderul '{output_dir}'. Asigură-te că ai rulat scriptul de generare mai întâi.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    tex_files = [f for f in os.listdir(output_dir) if f.endswith('.tex')]
    
    if not tex_files:
        print("Nu s-au găsit fișiere .tex în folderul 'output'.")
        return

    print("=== ÎNCEPERE VALIDARE FIȘIERE LATEX ===")
    for filename in tex_files:
        filepath = os.path.join(output_dir, filename)
        valideaza_fisier(filepath, json_data)
    print("=== VALIDARE COMPLETĂ ===")

if __name__ == "__main__":
    main()