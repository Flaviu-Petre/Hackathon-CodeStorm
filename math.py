import json
import os

def get_int_value(val):
    try:
        if val is None or str(val).strip() == "":
            return 0
        return int(float(val))
    except ValueError:
        return 0

def proceseaza_toate_materiile(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    discipline = data.get('Discipline', [])
    
    for materie in discipline:
        # Preluare date brute
        numar_credite = get_int_value(materie.get('Numarul_de_credite_Cr'))
        ore_curs = get_int_value(materie.get('Ore_AI'))
        ore_at = get_int_value(materie.get('Ore_AT'))
        ore_tc = get_int_value(materie.get('Ore_TC'))
        ore_aa = get_int_value(materie.get('Ore_AA'))
        
        # --- Calcule identice cu math.py original ---
        total_ore_semestru = numar_credite * 30
        numar_ore_curs_saptamana = ore_curs / 14
        numar_ore_sem_lab_proiect = ore_at + ore_tc + ore_aa
        numar_ore_sem_lab_proiect_string = f"0/{numar_ore_sem_lab_proiect}/0"
        
        total_ore_activitate_student = total_ore_semestru - ore_curs - numar_ore_sem_lab_proiect
        numar_ore_sem_lab_proiect_saptamana = numar_ore_sem_lab_proiect / 14
        numar_ore_sem_lab_proiect_saptamana_string = f"0/{int(numar_ore_sem_lab_proiect_saptamana)}/0"
        
        total_ore_plan_invatamant = ore_curs + ore_tc + ore_at
        numar_ore_saptamana = numar_ore_curs_saptamana + numar_ore_sem_lab_proiect_saptamana

        # --- Salvare în JSON (toate variabilele tale sunt aici) ---
        materie['Total_ore_semestru'] = total_ore_semestru
        materie['Numar_ore_curs_pe_saptamana'] = round(numar_ore_curs_saptamana, 2)
        materie['Numar_ore_seminar_laborator_proiect'] = numar_ore_sem_lab_proiect
        materie['Numar_ore_seminar_laborator_proiect_string'] = numar_ore_sem_lab_proiect_string
        materie['Total_ore_de_activitate_a_studentului'] = total_ore_activitate_student
        materie['Numar_ore_seminar_lab_proiect_pe_saptamana'] = round(numar_ore_sem_lab_proiect_saptamana, 2)
        materie['Numar_ore_seminar_lab_proiect_pe_saptamana_string'] = numar_ore_sem_lab_proiect_saptamana_string
        materie['Total_ore_din_planul_de_invatamant'] = total_ore_plan_invatamant
        materie['Numar_ore_saptamana'] = round(numar_ore_saptamana, 2)
        materie['Numarul_de_credite_Cr'] = numar_credite
        
        # Sincronizare pentru campurile folosite de ScriptLatex.py
        materie['Total_ore_didactice'] = ore_curs + ore_at + ore_aa
        materie['Total_ore_studiu_individual'] = total_ore_semestru - materie['Total_ore_didactice']

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Datele au fost calculate și salvate pentru {len(discipline)} discipline.")

if __name__ == "__main__":
    proceseaza_toate_materiile('date_extrase_pentru_template.json')