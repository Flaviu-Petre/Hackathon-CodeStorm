import subprocess
import sys
import os

def run_script(script_path):
    print(f"\n{'='*50}")
    print(f"🚀 RULEZ SCRIPTUL: {script_path}")
    print(f"{'='*50}\n")
    
    try:
        # Rulăm scriptul curent și afișăm output-ul în timp real
        result = subprocess.run(
            [sys.executable, script_path], 
            check=True,
            text=True
        )
        print(f"\n✅ SCRIPT COMPLETAT CU SUCCES: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ EROARE: Scriptul {script_path} a eșuat cu codul {e.returncode}.")
        print("Pipeline-ul a fost oprit.")
        sys.exit(1) # Oprim execuția dacă un pas eșuează
    except FileNotFoundError:
        print(f"\n❌ EROARE: Nu am putut găsi fișierul {script_path}.")
        sys.exit(1)

def main():
    print("🎓 PIPELINE GENERARE AUTOMATĂ FIȘE DE DISCIPLINĂ (ORCHESTRATOR)")
    
    # Definim ordinea exactă a scripturilor pe care vrei să le rulezi.
    pasi_pipeline = [
        "Extractor_Text.py",
        "math.py",
        "ScriptLatex.py",
        "validator.py"
    ]
    
    for script in pasi_pipeline:
        run_script(script)
        
    print("\n🎉 TOATE ETAPELE AU FOST PARCURSE CU SUCCES!")
        
    print("\n🎉 TOATE ETAPELE AU FOST PARCURSE CU SUCCES!")

if __name__ == "__main__":
    main()