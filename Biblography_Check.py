import json
from scholarly import scholarly

# Fișierul de input cu materiile
INPUT_JSON = "date_extrase_pentru_template.json"
# Fișierul final, filtrat și ordonat
OUTPUT_JSON = "bibliografie_google_scholar_filtrata.json"

def genereaza_si_filtreaza_bibliografie():
    print(f"📂 Citim materiile din {INPUT_JSON}...")
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            date = json.load(f)
    except FileNotFoundError:
        print(f"❌ Eroare: Nu am găsit {INPUT_JSON}. Asigură-te că există în folder.")
        return

    # Extragem doar numele materiilor din JSON
    materii = [disc["Denumirea_disciplinei"] for disc in date.get("Discipline", []) if "Denumirea_disciplinei" in disc]
    
    rezultat_json = {}
    total_eliminate = 0

    print(f"🔍 Am găsit {len(materii)} materii. Începem extragerea și filtrarea de pe Google Scholar...\n")

    for materie in materii:
        print(f"📚 Caut publicații pentru: {materie}")
        
        search_query = scholarly.search_pubs(materie)
        publicatii_materie = []
        
        # Limităm la 5 rezultate per materie
        for _ in range(5):
            try:
                pub = next(search_query)
                bib = pub.get('bib', {})
                
                titlu = bib.get('title', 'Titlu necunoscut')
                an = bib.get('pub_year', '0')
                autori = bib.get('author', 'Autori necunoscuți')
                url = pub.get('pub_url', 'Fără link valid')
                
                # Convertim anul în număr întreg
                try:
                    an_int = int(an)
                except ValueError:
                    an_int = 0
                    
                # 🔑 FILTRARE DIRECTĂ: Păstrăm și adăugăm doar dacă An_aparitie > 0
                if an_int > 0:
                    publicatii_materie.append({
                        "Titlu": titlu,
                        "Autori": autori,
                        "An_aparitie": an_int,
                        "Link": url
                    })
                else:
                    # Contorizăm publicațiile pe care le ignorăm
                    total_eliminate += 1
                    
            except StopIteration:
                break
            except Exception as e:
                print(f"   [!] Eroare la extragerea unei publicații: {e}")
                break
        
        # ORDONARE DESCRESCĂTOARE (cel mai nou primul)
        publicatii_sortate = sorted(publicatii_materie, key=lambda x: x["An_aparitie"], reverse=True)
        
        # Adăugăm în dicționarul final doar dacă au mai rămas publicații pentru această materie
        if publicatii_sortate:
            rezultat_json[materie] = publicatii_sortate

    # Salvăm rezultatul final într-un JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rezultat_json, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Procesul a fost finalizat cu succes!")
    print(f"🗑️ Au fost ignorate/eliminate {total_eliminate} publicații fără an valid (An_aparitie = 0).")
    print(f"💾 Bibliografia curată și ordonată a fost salvată în: {OUTPUT_JSON}")

if __name__ == "__main__":
    genereaza_si_filtreaza_bibliografie()