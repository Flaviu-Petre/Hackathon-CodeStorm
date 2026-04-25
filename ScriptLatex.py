import json
import os
from jinja2 import Environment

# Salvăm template-ul LaTeX direct în Python ca "raw string" (r"")
# Asta garantează că niciun backslash nu va fi pierdut la generare
LATEX_TEMPLATE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[romanian]{babel}
\usepackage{geometry}
\usepackage{xltabular}
\usepackage{multirow}
\usepackage{enumitem}
\geometry{a4paper, left=2cm, right=2cm, top=2cm, bottom=2cm}

% Setări pentru a face tabelele să arate mai bine
\renewcommand{\arraystretch}{1.3}
\setlist{nosep}

\begin{document}

\begin{center}
    \textbf{\Large FIŞA DISCIPLINEI}
\end{center}

\section*{1. Date despre program}
\noindent
\begin{xltabular}{\textwidth}{|l|X|}
\hline
1.1 Instituţia de învăţământ superior & \VAR{Date_despre_program.Institutia_de_invatamant_superior} \\ \hline
1.2 Facultatea & \VAR{Date_despre_program.Facultatea} \\ \hline
1.3 Departamentul & Matematică și Informatică \\ \hline
1.4 Domeniul de studii & \VAR{Date_despre_program.Domeniul_de_studii} \\ \hline
1.5 Ciclul de studii & \VAR{Date_despre_program.Ciclul_de_studii} \\ \hline
1.6 Programul de studiu / Calificarea & \VAR{Date_despre_program.Programul_de_studiu_Calificarea} \\ \hline
\end{xltabular}

\section*{2. Date despre disciplină}
\noindent
\begin{xltabular}{\textwidth}{|l|X|l|l|l|l|l|l|}
\hline
2.1 Denumirea disciplinei & \multicolumn{7}{l|}{\textbf{\VAR{Disciplina_curenta.Denumirea_disciplinei}}} \\ \hline
2.2 Titularul activităților de curs & \multicolumn{7}{l|}{(Completare manuală/ulterioară)} \\ \hline
2.3 Titularul activităților de seminar & \multicolumn{7}{l|}{(Completare manuală/ulterioară)} \\ \hline
2.4 Anul de studiu & \VAR{Disciplina_curenta.Anul_de_studiu} & 
2.5 Semestrul & \VAR{Disciplina_curenta.Semestrul} & 
2.6 Tipul de evaluare & \VAR{Disciplina_curenta.Forma_de_verificare_FV} & 
2.7 Regimul disciplinei & \VAR{Disciplina_curenta.C1_Obligativitate} \\ \hline
\end{xltabular}

\section*{3. Timpul total estimat (ore pe semestru al activităților didactice)}
\noindent
\begin{xltabular}{\textwidth}{|l|l|l|X|l|X|}
\hline
3.1 Număr de ore pe săptămână & & Din care: 3.2 curs & \VAR{Disciplina_curenta.Ore_AI} & 3.3 seminar/laborator & \VAR{Disciplina_curenta.Ore_AT} \\ \hline
3.4 Total ore din planul de învăţământ & \VAR{Disciplina_curenta.Total_ore_didactice} & Din care: 3.5 curs & \VAR{Disciplina_curenta.Ore_AI} & 3.6 seminar/laborator & \VAR{Disciplina_curenta.Ore_AT} \\ \hline
\multicolumn{6}{|l|}{Distribuţia fondului de timp: \textbf{\VAR{Disciplina_curenta.Numarul_de_credite_Cr} credite}} \\ \hline
\multicolumn{5}{|l|}{Studiul după manual, suport de curs, bibliografie şi notiţe} & \VAR{Disciplina_curenta.Ore_SI} \\ \hline
\multicolumn{5}{|l|}{Documentare suplimentară în bibliotecă, pe platforme, pe teren} &  \\ \hline
\multicolumn{5}{|l|}{Pregătire seminarii/laboratoare, teme, referate, portofolii şi eseuri} & \VAR{Disciplina_curenta.Ore_TC} \\ \hline
\multicolumn{5}{|l|}{Tutoriat} & \VAR{Disciplina_curenta.Ore_AT} \\ \hline
\multicolumn{5}{|l|}{Examinări} & \\ \hline
\multicolumn{5}{|l|}{Alte activități:} & \\ \hline
\multicolumn{3}{|l|}{3.7 Total ore studiu individual} & \multicolumn{3}{l|}{\VAR{Disciplina_curenta.Total_ore_studiu_individual}} \\ \hline
\multicolumn{3}{|l|}{3.8 Total ore pe semestru} & \multicolumn{3}{l|}{\VAR{Disciplina_curenta.Total_ore_semestru}} \\ \hline
\multicolumn{3}{|l|}{3.9 Numărul de credite} & \multicolumn{3}{l|}{\VAR{Disciplina_curenta.Numarul_de_credite_Cr}} \\ \hline
\end{xltabular}

\section*{4. Precondiţii (acolo unde este cazul)}
\noindent
\begin{xltabular}{\textwidth}{|l|X|}
\hline
4.1 de curriculum & \\ \hline
4.2 de competenţe & \\ \hline
\end{xltabular}

\section*{5. Condiţii (acolo unde este cazul)}
\noindent
\begin{xltabular}{\textwidth}{|l|X|}
\hline
5.1 De desfăşurare a cursului & • \\ \hline
5.2 De desfăşurare a seminarului/laboratorului & • \\ \hline
\end{xltabular}

\section*{6. Competenţele specifice acumulate}
\noindent
\begin{xltabular}{\textwidth}{|p{3.5cm}|X|}
\hline
Competenţe profesionale & 
\vspace{-0.3cm}
\begin{itemize}[leftmargin=*]
\BLOCK{ for comp in Competente_profesionale }
    \item \textbf{\VAR{comp.Competenta}}
    \begin{itemize}
    \BLOCK{ for rez in comp.Rezultate_invatare }
        \item \VAR{rez}
    \BLOCK{ endfor }
    \end{itemize}
\BLOCK{ endfor }
\end{itemize}
\vspace{-0.3cm}
\\ \hline
Competenţe transversale & 
\vspace{-0.3cm}
\begin{itemize}[leftmargin=*]
\BLOCK{ for comp in Competente_transversale }
    \item \textbf{\VAR{comp.Competenta}}
    \begin{itemize}
    \BLOCK{ for rez in comp.Rezultate_invatare }
        \item \VAR{rez}
    \BLOCK{ endfor }
    \end{itemize}
\BLOCK{ endfor }
\end{itemize}
\vspace{-0.3cm}
\\ \hline
\end{xltabular}

\section*{7. Obiectivele disciplinei}
\noindent
\begin{xltabular}{\textwidth}{|l|X|}
\hline
7.1 Obiectivul general al disciplinei & \\ \hline
7.2 Obiectivele specifice & \\ \hline
\end{xltabular}

\section*{8. Conţinuturi}
\noindent
\begin{xltabular}{\textwidth}{|X|l|l|}
\hline
\textbf{8.1 Curs} & \textbf{Metode de predare} & \textbf{Observaţii} \\ \hline
 & & \\ \hline
 & & \\ \hline
\multicolumn{3}{|l|}{\textbf{Bibliografie}} \\ \hline
\multicolumn{3}{|l|}{1. } \\ \hline
\end{xltabular}

\noindent
\begin{xltabular}{\textwidth}{|X|l|l|}
\hline
\textbf{8.2 Seminar/laborator} & \textbf{Metode de predare} & \textbf{Observaţii} \\ \hline
 & & \\ \hline
 & & \\ \hline
\multicolumn{3}{|l|}{\textbf{Bibliografie}} \\ \hline
\multicolumn{3}{|l|}{1. } \\ \hline
\end{xltabular}

\section*{9. Coroborarea conţinuturilor disciplinei cu aşteptările...}
\noindent (Descriere despre cum se potrivește materia cu cerințele angajatorilor și asociațiilor profesionale)
\vspace{0.5cm}

\section*{10. Evaluare}
\noindent
\begin{xltabular}{\textwidth}{|l|X|X|c|}
\hline
\textbf{Tip activitate} & \textbf{10.1 Criterii de evaluare} & \textbf{10.2 Metode de evaluare} & \textbf{10.3 Pondere nota finală} \\ \hline
10.4 Curs & & Examen (\VAR{Disciplina_curenta.Forma_de_verificare_FV}) & \% \\ \hline
10.5 Seminar/laborator & & & \% \\ \hline
\multicolumn{4}{|l|}{\textbf{10.6 Standard minim de performanţă}} \\ \hline
\multicolumn{4}{|l|}{• Obținerea notei 5 la evaluarea finală.} \\ \hline
\end{xltabular}

\vspace{1cm}
\noindent
\begin{xltabular}{\textwidth}{X X X}
\textbf{Data completării} & \textbf{Semnătura titularului de curs} & \textbf{Semnătura titularului de seminar} \\
......................... & ......................... & ......................... \\[1cm]
\textbf{Data avizării în departament} & & \textbf{Semnătura directorului de departament} \\
......................... & & ......................... \\
\end{xltabular}

\end{document}
"""

def setup_jinja_env():
    # Creăm mediul Jinja ignorând sistemul de fișiere
    return Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False
    )

def escape_latex(text):
    """
    Funcție de siguranță: previne erori de compilare dacă în JSON apar 
    caractere speciale pentru LaTeX (precum &, % sau _)
    """
    if not isinstance(text, str):
        return text
    
    # Caracterele _ și % și & pot "rupe" un compilator de LaTeX. Le prefixăm cu \
    chars_to_escape = {'&': r'\&', '%': r'\%', '_': r'\_'}
    return "".join(chars_to_escape.get(c, c) for c in text)

def format_data(data):
    """Parcurge structura dicționarului și aplică escape pe valorile text."""
    if isinstance(data, dict):
        return {k: format_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_data(v) for v in data]
    else:
        return escape_latex(data)

def generate_tex(discipline_data, program_data, prof_comp, trans_comp):
    env = setup_jinja_env()
    # Randăm template-ul direct din textul definit mai sus
    template = env.from_string(LATEX_TEMPLATE)

    # Evităm erori dacă un text din JSON conține _ (underscore) sau alte semne ciudate
    safe_discipline = format_data(discipline_data)
    safe_program = format_data(program_data)
    safe_prof_comp = format_data(prof_comp)
    safe_trans_comp = format_data(trans_comp)

    rendered_tex = template.render(
        Date_despre_program=safe_program,
        Disciplina_curenta=safe_discipline,
        Competente_profesionale=safe_prof_comp,
        Competente_transversale=safe_trans_comp
    )

    file_name = discipline_data['Denumirea_disciplinei'].replace(" ", "_")
    # Ne asigurăm că eliminăm eventuale semne ciudate din numele fișierului
    safe_file_name = "".join(c for c in file_name if c.isalnum() or c in ('_', '-'))
    tex_filename = os.path.join("output", f"{safe_file_name}.tex")

    try:
        with open(tex_filename, "w", encoding="utf-8") as f:
            f.write(rendered_tex)
        print(f"Succes: Fișier TEX valid generat pentru {discipline_data['Denumirea_disciplinei']}")
    except Exception as e:
        print(f"Eroare: A eșuat generarea TEX pentru {discipline_data['Denumirea_disciplinei']}")
        print(f"Detalii eroare: {e}")

def main():
    if not os.path.exists('output'):
        os.makedirs('output')

    with open('date_extrase_pentru_template.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    program_info = data['Date_despre_program']
    prof_comp = data['Competente_profesionale']
    trans_comp = data['Competente_transversale']
    discipline_list = data['Discipline']

    for disc in discipline_list:
        # Prevenim valorile lipsă convertindu-le direct la 0
        chei_ore = ['Ore_AI', 'Ore_AT', 'Ore_TC', 'Ore_AA', 'Ore_SI']
        for key in chei_ore:
            val = disc.get(key, "0")
            disc[key] = int(val) if str(val).strip() else 0
                
        # disc['Numarul_de_credite_Cr'] = int(disc['Numarul_de_credite_Cr'])
        val_credite = disc.get('Numarul_de_credite_Cr', "0")
        disc['Numarul_de_credite_Cr'] = int(val_credite) if str(val_credite).strip() else 0
        
        # Matematica pentru distribuția timpului (25 ore/credit)
        ore_didactice = disc['Ore_AI'] + disc['Ore_AT'] + disc['Ore_AA']
        ore_totale = disc['Numarul_de_credite_Cr'] * 25
        ore_individuale = ore_totale - ore_didactice
        
        disc['Total_ore_didactice'] = ore_didactice
        disc['Total_ore_semestru'] = ore_totale
        disc['Total_ore_studiu_individual'] = ore_individuale

        generate_tex(disc, program_info, prof_comp, trans_comp)

if __name__ == "__main__":
    main()