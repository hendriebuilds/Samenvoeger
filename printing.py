import os
import subprocess
import sys

def find_acrobat() -> str | None:
    if sys.platform != "win32":
        return None
    import winreg
    for exe_name in ("Acrobat.exe", "AcroRd32.exe"):
        try:
            key = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
                path, _ = winreg.QueryValueEx(k, "")
                if path:
                    return path
        except OSError:
            pass
    fallbacks = [
        r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
        r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
        r"C:\Program Files\Adobe\Acrobat 2020\Acrobat\Acrobat.exe",
    ]
    for path in fallbacks:
        if os.path.exists(path):
            return path
    return None

def print_with_acrobat(pdf_path: str) -> bool:
    acrobat = find_acrobat()
    if not acrobat:
        return False
    subprocess.Popen([acrobat, "/p", pdf_path])
    return True
