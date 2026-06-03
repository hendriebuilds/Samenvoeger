Claude Code — Samenvoeger instructies
Versiebeheer

Semantic versioning (MAJOR.MINOR.PATCH)
Pas versienummer aan in pyproject.toml na elke sessie
Vermeld versienummer in commit message

Voorbeeld: feat: drag-and-drop ondersteuning — v1.1.0
Voorbeeld: fix: crash bij lege bronmap — v1.0.1


Releasen = taggen: git tag v1.1.0 && git push origin v1.1.0

Tech stack — nooit afwijken

Runtime: Python 3.11, tkinter (stdlib), pypdf
Build: PyInstaller, Samenvoeger.spec
CI/CD: GitHub Actions — zie .github/workflows/build.yml
Geen externe UI-frameworks (geen customtkinter, geen Qt) tenzij expliciet gevraagd
Geen netwerk/API-dependencies

Projectstructuur
samenvoeger/
├── .github/
│   └── workflows/
│       └── build.yml         # GitHub Actions build workflow
├── PDFMerger.py              # Hoofdapplicatie
├── Samenvoeger.spec          # PyInstaller build spec
├── icon.ico                  # App-icoon
├── pyproject.toml            # Versie en dependencies
├── logs/                     # Runtime logs (gitignore)
└── dist/                     # Build output (gitignore)
Werkwijze

Features zijn uitgewerkt via Claude — lees het plan goed door
Stel vragen als iets onduidelijk is — ga niet gokken
Implementeer, test lokaal, verhoog versienummer in pyproject.toml
Commit met versienummer in de message
Taggen doet Hendrie zelf — niet automatisch pushen

Aandachtspunten

Build-target is Windows .exe via GitHub Actions Windows runner
Bij wijzigingen aan dependencies: ook Samenvoeger.spec bijwerken (hiddenimports, excludes) én de pip install regel in build.yml
config.env.enc en key.key zijn legacy-bestanden — negeren, niet opnemen in nieuwe code, toevoegen aan .gitignore