import json

def get_int_value(val):
    """Transformă o valoare string într-un număr întreg. Returnează 0 dacă e gol."""
    try:
        if val is None or val == "":
            return 0
        return int(val)
    except ValueError:
        return 0

def calculeaza_date_materie(json_path, cod_materie):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    discipline = data.get('Discipline', [])
    
    materie = None
    for d in discipline:
        if d.get('Cod_disciplina') == cod_materie:
            materie = d
            break
            
    if not materie:
        return {"Eroare": f"Materia cu codul '{cod_materie}' nu a fost gasita."}
        

    numar_credite = get_int_value(materie.get('Numarul_de_credite_Cr'))
    ore_curs = get_int_value(materie.get('Ore_AI'))
    ore_at = get_int_value(materie.get('Ore_AT'))
    ore_tc = get_int_value(materie.get('Ore_TC'))
    ore_aa = get_int_value(materie.get('Ore_AA'))
    
    total_ore_semestru = numar_credite * 30
    
    numar_ore_curs_saptamana = ore_curs / 14
    
    numar_ore_sem_lab_proiect = ore_at + ore_tc + ore_aa

    numar_ore_sem_lab_proiect_string = f"0/{numar_ore_sem_lab_proiect}/0"
    
    total_ore_activitate_student = total_ore_semestru - ore_curs - numar_ore_sem_lab_proiect
    
    numar_ore_sem_lab_proiect_saptamana = numar_ore_sem_lab_proiect / 14

    numar_ore_sem_lab_proiect_saptamana_string = f"0/{int(numar_ore_sem_lab_proiect_saptamana)}/0"

    total_ore_plan_invatamant = ore_curs + ore_tc + ore_at

    numar_ore_saptamana = numar_ore_curs_saptamana + numar_ore_sem_lab_proiect_saptamana
    

    rezultate = {
        "Denumirea_disciplinei": materie.get('Denumirea_disciplinei'),
        "Cod_disciplina": cod_materie,
        "Total_ore_pe_semestru": total_ore_semestru,
        "Numar_ore_curs_pe_saptamana": round(numar_ore_curs_saptamana, 2),
        "Numar_ore_seminar_laborator_proiect": numar_ore_sem_lab_proiect,
        "Numar_ore_seminar_laborator_proiect_string":numar_ore_sem_lab_proiect_string,
        "Total_ore_de_activitate_a_studentului": total_ore_activitate_student,
        "Numar_ore_seminar_lab_proiect_pe_saptamana": round(numar_ore_sem_lab_proiect_saptamana, 2),
        "Numar_ore_seminar_lab_proiect_pe_saptamana_string":numar_ore_sem_lab_proiect_saptamana_string,
        "Total_ore_din_planul_de_invatamant": total_ore_plan_invatamant,
        "Numar_ore_saptamana": numar_ore_saptamana,
        "Numar_credite": numar_credite
    }
    
    return rezultate


if __name__ == "__main__":
    fisier_json = 'date_extrase_pentru_template.json'
    cod_dorit = 'AP001-ID'
    
    rezultat = calculeaza_date_materie(fisier_json, cod_dorit)
    
    print(json.dumps(rezultat, indent=4, ensure_ascii=False))