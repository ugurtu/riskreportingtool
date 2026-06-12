# Risk Profile Generator

A self-hosted web tool for creating standardized IT risk assessment documents. Fill in a structured form, preview the result in real time, and download a professionally typeset PDF - compiled from LaTeX for consistent, print-ready output.

Built for information security teams, IT risk managers, and compliance officers who need to produce risk documentation aligned with frameworks like BSI IT-Grundschutz.

## What it does

The tool generates a single-page risk profile PDF containing:

- **Header** - Risk title, owner, review date, and audit interval
- **Intervals legend** - Color-coded review frequency table (monthly through biennial)
- **CIA classification** - Confidentiality, Integrity, and Availability ratings
- **Risk description** - Free-text description of the Risk
- **Risk assessment** - Analysis of potential impact and likelihood
- **Risk matrix** - 4x4 likelihood-vs-impact heatmap with a positioned marker
- **Conclusion** - Summary judgment informed by the matrix position
- **Risk reduction measures** - Two-column table of risk factors and their corresponding countermeasures
- **Risk distribution** - Single-column table listing risk distribution items
- **Residual risk** - Residual risk statement after measures are applied
- **Risk acceptance** - Formal risk acceptance statement

All sections render with consistent blue header bars, alternating row shading, and proper typographic conventions.

## How it works

The interface is a split-pane layout: the form on the left, a live PDF preview on the right. Changes are reflected instantly - press Enter in any field to recompile. The backend receives form data, builds a LaTeX document programmatically (using `fcolorbox` for headers, `tikz` for the risk matrix, `tabular` for data tables), compiles it with `pdflatex`, and streams the PDF back to the browser.

## Features

- **Live preview** - Press Enter or Ctrl+Enter to regenerate the PDF without leaving the form
- **Interactive risk matrix** - Click any cell in the 4x4 grid to place the risk marker
- **Dynamic tables** - Add and remove rows for risk measures and distribution items
- **JSON export/import** - Save the entire form state as JSON, reload it later or share it with colleagues
- **PDF download** - One-click download of the compiled document

## Prerequisites

Two things need to be installed on your machine: Python and LaTeX.

### 1. Install LaTeX

**macOS**
```bash
brew install --cask mactex-no-gui
```

**Ubuntu / Debian**
```bash
sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
```

**Windows**

Download and install MiKTeX from [miktex.org/download](https://miktex.org/download). It auto-installs missing packages on first use.

### 2. Install Python (3.10+)

Download from [python.org](https://www.python.org/downloads/) or use your system package manager.

## Quick Start

```bash
# Clone or copy the project
cd risikoapp

# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install flask

# Run
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

## File Structure

```
risikoapp/
├── app.py                # Flask backend, LaTeX generation, PDF compilation
├── templates/
│   └── index.html        # Frontend: form, preview pane, JSON import/export
└── README.md
```

## Keyboard Shortcuts

| Shortcut              | Action                              |
|-----------------------|-------------------------------------|
| Enter (in any field)  | Generate PDF preview                |
| Ctrl/Cmd + Enter      | Generate PDF preview (from anywhere)|
| Click logo            | Toggle file menu                    |

## Technology

- **Backend** - Python / Flask
- **PDF engine** - LaTeX (pdflatex) with TikZ, colortbl, fcolorbox
- **Frontend** - Vanilla HTML/CSS/JS, no frameworks

## Roadmap

A future version will ship as a Docker container, bundling Python and TeX Live into a single image so no local installation is required.