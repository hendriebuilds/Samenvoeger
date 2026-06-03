import os
import sys
import datetime
import re
import threading
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from tkinterdnd2 import TkinterDnD, DND_FILES
from settings import load_settings, save_settings
from printing import print_with_acrobat

# =========================================================
# INSTELLINGEN
# =========================================================
RETRY_COUNT = 3

# =========================================================
# HULPFUNCTIES
# =========================================================
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def setup_logging():
    if getattr(sys, 'frozen', False):
        log_dir = Path(os.path.dirname(sys.executable)) / "logs"
    else:
        log_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"pdfmerger_{datetime.date.today():%Y-%m-%d}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")]
    )

setup_logging()

def is_merged_bestand(naam: str) -> bool:
    return bool(re.search(r'_Merged.*\.pdf$', naam, re.IGNORECASE))

def sorteer_op_id(f: Path) -> float:
    match = re.match(r'^(\d+)', f.name)
    return int(match.group(1)) if match else float('inf')

def get_unieke_bestandsnaam(pad: Path) -> Path:
    if not pad.exists():
        return pad
    base, ext = pad.stem, pad.suffix
    teller = 1
    while True:
        nieuw = pad.parent / f"{base}({teller}){ext}"
        if not nieuw.exists():
            return nieuw
        teller += 1

# =========================================================
# GUI
# =========================================================
class PDFMergerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Samenvoeger")
        self.geometry("700x305")
        self.resizable(False, False)
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass
        self.geselecteerde_bestanden: list = []
        self._settings = load_settings()
        self._build_ui()
        self._laad_opgeslagen_paden()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Bron:").grid(row=0, column=0, sticky="w", **pad)
        self.input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.input_var).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Map", command=self._kies_bronmap).grid(row=0, column=2, **pad)
        ttk.Button(frame, text="Bestanden", command=self._kies_bestanden).grid(row=0, column=3, **pad)

        ttk.Label(frame, text="Doelmap:").grid(row=1, column=0, sticky="w", **pad)
        self.doel_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.doel_var).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Selecteer", command=self._kies_doelmap).grid(row=1, column=2, columnspan=2, **pad)

        self.start_btn = ttk.Button(frame, text="▶  Start Verwerking", command=self._start)
        self.start_btn.grid(row=2, column=1, pady=(12, 5))

        self.print_var = tk.BooleanVar(value=self._settings.get("print_after_merge", False))
        ttk.Checkbutton(
            frame, text="Direct afdrukken na samenvoegen", variable=self.print_var,
            command=self._sla_print_instelling_op
        ).grid(row=3, column=1, pady=(0, 6))

        self.progress = ttk.Progressbar(frame, length=380, mode="determinate", maximum=100)
        self.progress.grid(row=4, column=0, columnspan=4, padx=10, pady=4, sticky="ew")

        self.status_lbl = tk.Label(frame, text="Selecteer een bronmap of PDF-bestanden, en een doelmap", fg="gray", anchor="center")
        self.status_lbl.grid(row=5, column=0, columnspan=4, pady=2)

        ttk.Button(frame, text="Sluiten", command=self.destroy).grid(row=6, column=1, pady=(8, 0))

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)
        self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self._on_drag_leave)

    def _parseer_drop_paden(self, data: str) -> list[Path]:
        import re
        tokens = re.findall(r'\{[^}]*\}|[^\s]+', data)
        return [Path(t.strip('{}')) for t in tokens if t.strip('{}')]

    def _on_drag_enter(self, event):
        self.status_lbl.config(text="Loslaten om toe te voegen...", fg="blue")

    def _on_drag_leave(self, event):
        self.status_lbl.config(text="Selecteer een bronmap of PDF-bestanden, en een doelmap", fg="gray")

    def _on_drop(self, event):
        self.status_lbl.config(text="Selecteer een bronmap of PDF-bestanden, en een doelmap", fg="gray")
        paden = self._parseer_drop_paden(event.data)
        if not paden:
            return

        toegevoegd = 0
        niet_pdf = 0
        bestaande_paden = {p for p in self.geselecteerde_bestanden}

        for pad in paden:
            if pad.is_dir():
                for pdf in pad.glob("*.pdf"):
                    if pdf not in bestaande_paden and not is_merged_bestand(pdf.name):
                        self.geselecteerde_bestanden.append(pdf)
                        bestaande_paden.add(pdf)
                        toegevoegd += 1
            elif pad.suffix.lower() == '.pdf':
                if pad not in bestaande_paden:
                    self.geselecteerde_bestanden.append(pad)
                    bestaande_paden.add(pad)
                    toegevoegd += 1
            else:
                niet_pdf += 1

        if niet_pdf and not toegevoegd:
            self._set_status("Alleen PDF-bestanden worden ondersteund", "red")
            return

        totaal = len(self.geselecteerde_bestanden)
        if totaal:
            tekst = f"{totaal} PDF-bestand(en) geselecteerd"
            if niet_pdf:
                tekst += f"  |  {niet_pdf} niet-PDF overgeslagen"
            self.input_var.set(tekst)
            self._set_status(tekst, "gray")

    def _kies_map(self, var: tk.StringVar):
        pad = filedialog.askdirectory()
        if pad:
            var.set(pad)

    def _kies_bronmap(self):
        pad = filedialog.askdirectory()
        if pad:
            self.geselecteerde_bestanden = []
            self.input_var.set(pad)
            self._settings["last_source_dir"] = pad
            save_settings(self._settings)

    def _kies_doelmap(self):
        pad = filedialog.askdirectory()
        if pad:
            self.doel_var.set(pad)
            self._settings["last_output_dir"] = pad
            save_settings(self._settings)

    def _kies_bestanden(self):
        bestanden = filedialog.askopenfilenames(
            title="Selecteer PDF-bestanden",
            filetypes=[("PDF-bestanden", "*.pdf"), ("Alle bestanden", "*.*")]
        )
        if bestanden:
            self.geselecteerde_bestanden = [Path(b) for b in bestanden]
            self.input_var.set(f"{len(bestanden)} PDF-bestand(en) geselecteerd")
            self._settings["last_source_dir"] = str(Path(bestanden[0]).parent)
            save_settings(self._settings)

    def _sla_print_instelling_op(self):
        self._settings["print_after_merge"] = self.print_var.get()
        save_settings(self._settings)

    def _laad_opgeslagen_paden(self):
        bron = self._settings.get("last_source_dir", "")
        if bron and Path(bron).is_dir():
            self.input_var.set(bron)
        doel = self._settings.get("last_output_dir", "")
        if doel and Path(doel).is_dir():
            self.doel_var.set(doel)

    def _set_status(self, tekst: str, kleur: str = "gray"):
        self.after(0, lambda: self.status_lbl.config(text=tekst, fg=kleur))

    def _set_progress(self, waarde: float):
        self.after(0, lambda: self.progress.config(value=waarde))

    def _start(self):
        if not self.input_var.get() or not self.doel_var.get():
            self._set_status("Selecteer eerst een bron en doelmap", "red")
            return
        self.after(0, lambda: self.start_btn.config(state="disabled"))
        self.after(0, lambda: self.progress.config(value=0))
        threading.Thread(target=self._verwerk, daemon=True).start()

    def _verwerk(self):
        try:
            self._verwerk_intern()
        except Exception as e:
            logging.error(f"Verwerking afgebroken: {e}")
            self._set_status(f"Fout: {e}", "red")
        finally:
            self.after(0, lambda: self.start_btn.config(state="normal"))

    def _verwerk_intern(self):
        doel_path = Path(self.doel_var.get())
        datum_str = datetime.date.today().strftime("%Y-%m-%d")

        # 1. PDF's verzamelen
        if self.geselecteerde_bestanden:
            pdf_files = sorted(
                [f for f in self.geselecteerde_bestanden if not is_merged_bestand(f.name)],
                key=sorteer_op_id
            )
            logging.info(f"=== START | {len(self.geselecteerde_bestanden)} geselecteerde bestanden | doelmap={doel_path} ===")
        else:
            input_path = Path(self.input_var.get())
            logging.info(f"=== START | bronmap={input_path} | doelmap={doel_path} ===")
            self._set_status("Zoeken naar PDF-bestanden...")
            pdf_files = sorted(
                [f for f in input_path.glob("*.pdf") if not is_merged_bestand(f.name)],
                key=sorteer_op_id
            )

        totaal = len(pdf_files)
        if totaal == 0:
            self._set_status("Geen PDF-bestanden gevonden", "red")
            logging.warning("Geen PDF-bestanden gevonden")
            return

        logging.info(f"{totaal} PDF's gevonden")

        # 2. Bestandsnaam bepalen
        merged_path = get_unieke_bestandsnaam(doel_path / f"{datum_str}_Merged.pdf")
        logging.info(f"Doelbestand: {merged_path.name}")

        # 3. Samenvoegen
        merger = PdfWriter()
        mislukt = []
        for index, pdf in enumerate(pdf_files, start=1):
            self._set_status(f"Samenvoegen: bestand {index} van {totaal}")
            self._set_progress((index / totaal) * 80)
            try:
                PdfReader(str(pdf))
                merger.append(str(pdf))
                logging.info(f"Toegevoegd: {pdf.name}")
            except Exception as e:
                mislukt.append(pdf.name)
                logging.warning(f"Overgeslagen: {pdf.name} — {e}")

        if len(merger.pages) == 0:
            self._set_status("Geen geldige PDF's om samen te voegen", "red")
            logging.error("Geen geldige PDF-pagina's gevonden")
            return

        # 4. Wegschrijven naar doelmap
        self._set_status("Opslaan naar doelmap...")
        doel_path.mkdir(parents=True, exist_ok=True)
        merger.write(str(merged_path))
        merger.close()

        # 5. Post-merge validatie
        try:
            PdfReader(str(merged_path))
            logging.info(f"Validatie geslaagd: {merged_path.name}")
        except Exception as e:
            merged_path.unlink(missing_ok=True)
            self._set_status("Samengevoegd bestand is ongeldig", "red")
            logging.error(f"Post-merge validatie mislukt: {e}")
            return

        self._set_progress(100)
        samenvatting = f"Klaar — {merged_path.name}  ({totaal - len(mislukt)}/{totaal} bestanden)"
        if mislukt:
            samenvatting += f"  |  {len(mislukt)} overgeslagen"
        self._set_status(samenvatting, "green")
        logging.info(f"=== EINDE | {samenvatting} ===")

        if self.print_var.get():
            if print_with_acrobat(str(merged_path)):
                logging.info(f"Afdrukken gestart: {merged_path.name}")
            else:
                logging.warning("Afdrukken mislukt: Adobe Acrobat niet gevonden")
                self.after(0, lambda: tk.messagebox.showwarning(
                    "Afdrukken niet mogelijk",
                    "Adobe Acrobat niet gevonden. Afdrukken niet mogelijk."
                ))


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
