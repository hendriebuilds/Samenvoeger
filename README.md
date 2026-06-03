# Samenvoeger

PDF-bestanden samenvoegen via een eenvoudige Windows-applicatie.

---

## Lokaal gebruiken

1. Download `Samenvoeger-v*.zip` van de [Releases](../../releases)-pagina.
2. Pak het zip-bestand uit naar een map naar keuze.
3. Start `Samenvoeger.exe`.
4. Selecteer een bronmap of losse PDF-bestanden, kies een doelmap en klik **Start Verwerking**.

---

## Intune deployment

### Win32-app toevoegen

1. Ga naar [Intune-beheercentrum](https://intune.microsoft.com) → **Apps** → **Alle apps** → **Toevoegen**.
2. Kies app-type **Windows-app (Win32)**.
3. Upload `Samenvoeger-v*.intunewin` als app-pakket.

### App-eigenschappen invullen

| Veld | Waarde |
|---|---|
| Naam | Samenvoeger |
| Versie | bijv. `1.0.0` |
| Installatieopdracht | `powershell.exe -ExecutionPolicy Bypass -File install.ps1` |
| Verwijderopdracht | `powershell.exe -ExecutionPolicy Bypass -File uninstall.ps1` |
| Installatiegedrag | Systeem |

### Detectieregel instellen

- Type: **Register**
- Sleutelpad: `HKEY_LOCAL_MACHINE\Software\Samenvoeger`
- Waardenaam: `Version`
- Detectiemethode: Sleutelwaarde bestaat

### Toewijzing

Wijs de app toe aan de gewenste gebruikers- of apparaatgroep via het tabblad **Toewijzingen**.

---

## Nieuwe versie uitrollen

1. Verhoog het versienummer in `pyproject.toml`.
2. Commit en tag:
   ```
   git tag v1.x.x && git push origin v1.x.x
   ```
3. Wacht tot GitHub Actions klaar is — de nieuwe `.zip` en `.intunewin` verschijnen automatisch op de Releases-pagina.
4. Ga in Intune naar de app → **Eigenschappen** → upload het nieuwe `.intunewin`-bestand en pas het versienummer aan.
