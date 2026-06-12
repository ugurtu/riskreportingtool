import os
import subprocess
import tempfile
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)


def escape_latex(s):
    if not s:
        return ""
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    return s


def header_bar(text):
    """Full-width blue header bar using fcolorbox."""
    return (
            "\\noindent\\fcolorbox{headerblue}{headerblue}"
            "{\\parbox{\\dimexpr\\textwidth-2\\fboxsep-2\\fboxrule}"
            "{\\textcolor{white}{\\textbf{" + text + "}}}}\n"
    )


def build_risk_table(col1_values, col2_values):
    """Build a LaTeX table, alternating white/gray rows, no column header row."""
    tex = "\\begin{tabular}{p{0.42\\textwidth}p{0.52\\textwidth}}\n"
    rows = list(zip(col1_values, col2_values))
    if not rows:
        tex += " & \\\\\n"
    else:
        for i, (c1, c2) in enumerate(rows):
            bg = "\\rowcolor{cellgray}" if i % 2 == 1 else "\\rowcolor{white}"
            tex += f"{bg}{escape_latex(c1)} & {escape_latex(c2)} \\\\\n"
    tex += "\\end{tabular}\n"
    return tex


def build_latex(data, col1_values, col2_values, col1_header, col2_header, div_col1_values=None):
    owner = escape_latex(data.get("owner", ""))
    review_date = escape_latex(data.get("review_date", ""))
    interval = escape_latex(data.get("interval", ""))
    risk_title = escape_latex(data.get("risk_title", ""))
    cia_c = escape_latex(data.get("cia_c", "1"))
    cia_i = escape_latex(data.get("cia_i", "3"))
    cia_a = escape_latex(data.get("cia_a", "4"))

    matrix_row = int(data.get("matrix_row", "0"))
    matrix_col = int(data.get("matrix_col", "2"))
    marker_x = matrix_col + 0.5
    marker_y = matrix_row + 0.5

    desc_paras = "\n\n".join(
        p.strip() for p in data.get("description", "").split("\n") if p.strip()
    )
    assess_paras = "\n\n".join(
        p.strip() for p in data.get("assessment", "").split("\n") if p.strip()
    )
    conclusion = escape_latex(data.get("conclusion", ""))
    residual_risk = "\n\n".join(p.strip() for p in data.get("residualrisk", "").split("\n") if p.strip())
    risk_acceptance = "\n\n".join(p.strip() for p in data.get("riskacceptance", "").split("\n") if p.strip())

    risk_table_tex = build_risk_table(col1_values, col2_values)

    tex = r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[top=2cm,bottom=2cm,left=2cm,right=2cm]{geometry}
\usepackage{xcolor}
\usepackage{colortbl}
\usepackage{array}
\usepackage{multirow}
\usepackage{tikz}
\usepackage{parskip}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{microtype}
\usepackage[format=plain,labelfont=it,textfont=it]{caption}

\definecolor{headerblue}{RGB}{46, 64, 83}
\definecolor{lightblue}{RGB}{189,215,238}
\definecolor{titlegray}{RGB}{64,64,64}
\definecolor{yellowhl}{RGB}{255,192,0}
\definecolor{red1}{RGB}{220,20,20}
\definecolor{orange1}{RGB}{255,140,0}
\definecolor{yellow1}{RGB}{255,230,0}
\definecolor{green1}{RGB}{0,160,70}
\definecolor{lightgreen}{RGB}{130,190,60}
\definecolor{cellgray}{RGB}{242,242,242}

\pagestyle{empty}
\setlength{\parindent}{0pt}

\begin{document}

"""

    # Title
    tex += "{\\bfseries\\color{headerblue} Risk Assessment Report - " + risk_title + "\\hfill \\small \\today }\n\n"
    tex += "\\vspace{0.3cm}\n\n"

    # Header table (owner, review, interval)
    tex += "\\noindent\\fcolorbox{headerblue}{headerblue}{\\parbox{\\dimexpr\\textwidth-2\\fboxsep-2\\fboxrule}{"
    tex += "\\begin{tabular}{@{}p{.30\\textwidth}p{.30\\textwidth}p{.30\\textwidth}@{}}\n"
    tex += "\\textcolor{white}{\\textbf{Risk Owner}} & \\textcolor{white}{\\textbf{Last Review}} & \\textcolor{white}{\\textbf{Next Interval}} \\\\\n"
    tex += "\\end{tabular}}}\n\n"
    tex += "\\begin{tabular}{@{}p{.30\\textwidth}p{.30\\textwidth}p{.30\\textwidth}@{}}\n"
    tex += "\\textbf{" + owner + "} & " + review_date + " & \\textit{" + interval + "} \\\\\n"
    tex += "\\end{tabular}\n\n\\vspace{0.5cm}\n\n"

    # Intervals + CIA
    tex += r"""
\begin{minipage}[t]{0.45\textwidth}
\begin{tabular}{p{0.45cm}p{3.5cm}}
\multicolumn{2}{l}{\cellcolor{headerblue}\textcolor{white}{\textbf{Intervals}}} \\
\cellcolor{red1} & Monthly \\
\cellcolor{orange1} & $\frac{1}{4}$ Yearly \\
\cellcolor{yellow1} & $\frac{1}{2}$ Yearly \\
\cellcolor{lightgreen} & Yearly \\
\cellcolor{green1} & Every 2 Years \\
\end{tabular}
\end{minipage}
\hfill
\begin{minipage}[t]{0.50\textwidth}
\raggedleft
\vspace{-1.53cm}
\begin{tabular}{p{4.5cm} p{0.7cm} p{0.7cm} p{0.7cm}}
\cellcolor{headerblue}\textcolor{white}{\textbf{Risk of Compromise}} & \textbf{C} & \textbf{I} & \textbf{A} \\
"""
    tex += " & " + cia_c + " & " + cia_i + " & " + cia_a + " \\\\\n"
    tex += "\\end{tabular}\n\\end{minipage}\n\n\\vspace{0.5cm}\n\n"

    # Description
    tex += header_bar("Description of the Risk")
    tex += "\n\n\\vspace{0.1cm}\\noindent\n"
    tex += desc_paras + "\n\n\\vspace{0.3cm}"

    # Risk Assessment
    tex += header_bar("Risk Assessment")
    tex += "\n\n\\vspace{0.1cm}\\noindent\n"
    tex += assess_paras + "\n\n"

    # Risk matrix
    tex += "\\begin{figure}[!h]\\centering\\begin{tikzpicture}[scale=1.4]\n"
    row_labels = ['highly unlikely', 'unlikely', 'likely', 'constantly']
    col_labels = ['low', 'medium', 'high', 'very high']
    for i, lbl in enumerate(row_labels):
        tex += f"  \\node[anchor=east,font=\\small] at (0,{i + 0.5}) {{{lbl}}};\n"
    for j, lbl in enumerate(col_labels):
        tex += f"  \\node[anchor=north,font=\\small] at ({j + 0.5},-0.05) {{{lbl}}};\n"

    colors = [
        ['green1', 'lightgreen', 'yellow1', 'yellow1'],
        ['lightgreen', 'yellow1', 'orange1', 'orange1'],
        ['yellow1', 'orange1', 'orange1', 'red1'],
        ['yellow1', 'orange1', 'red1', 'red1'],
    ]
    for row in range(4):
        for col in range(4):
            tex += f"  \\fill[{colors[row][col]}] ({col},{row}) rectangle ({col + 1},{row + 1});\n"

    tex += "  \\draw[thick] (0,0) grid (4,4);\n"
    tex += f"  \\draw[thick,fill=white] ({marker_x},{marker_y}) circle (0.2);\n"
    tex += "\\end{tikzpicture}\\caption{Risk matrix for " + risk_title + "}\\end{figure}\n\n"

    tex += "\n\n\\vspace{0.1cm}\\noindent\n\n"
    tex += conclusion + "\n\n"

    # Risk reduction table
    tex += header_bar("Risk Mitigation Measures")
    tex += "\n\n\\vspace{0.1cm}\\noindent\n"
    tex += risk_table_tex
    tex += "\n\n"

    # Single-column Risikoverteilung table
    if div_col1_values:
        tex += header_bar("Risk Diversification")
        tex += "\n\n\\vspace{0.1cm}\\noindent\n"
        tex += "\\begin{tabular}{p{\\dimexpr\\textwidth-2\\tabcolsep}}\n"
        for i, val in enumerate(div_col1_values):
            bg = "\\rowcolor{cellgray}" if i % 2 == 1 else "\\rowcolor{white}"
            tex += f"{bg}{escape_latex(val)} \\\\\n"
        tex += "\\end{tabular}\n\n"

    # Residual risk
    if residual_risk:
        tex += header_bar("Rest Risk")
        tex += "\n\n\\vspace{0.1cm}\\noindent\n"
        tex += residual_risk + "\n\n"

    # Risk acceptance
    if risk_acceptance:
        tex += header_bar("Risk Acceptance")
        tex += "\n\n\\vspace{0.1cm}\\noindent\n"
        tex += f"\\textbf{{{risk_acceptance}}}" + "\n\n"

    tex += "\\end{document}\n"
    return tex


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.form.to_dict()

    col1_values = request.form.getlist("risk_col1[]")
    col2_values = request.form.getlist("risk_col2[]")
    col1_header = data.get("risk_col1_header", "Factor")
    col2_header = data.get("risk_col2_header", "Measure / Comment")

    max_len = max(len(col1_values), len(col2_values), 1)
    col1_values += [""] * (max_len - len(col1_values))
    col2_values += [""] * (max_len - len(col2_values))

    div_col1_values = request.form.getlist("div_col1[]")
    latex_source = build_latex(data, col1_values, col2_values, col1_header, col2_header, div_col1_values)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "document.tex")
        pdf_path = os.path.join(tmpdir, "document.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
            capture_output=True, text=True
        )

        if not os.path.exists(pdf_path):
            log = result.stdout + result.stderr
            return jsonify({"error": "LaTeX compilation failed", "log": log[-3000:]}), 500

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    title = data.get("risk_title", "dokument").replace(" ", "_")
    out_path = f"/tmp/risiko_{title}.pdf"
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    return send_file(out_path, as_attachment=True,
                     download_name=f"Risikosteckbrief_{title}.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
