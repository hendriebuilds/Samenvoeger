# Samenvoeger

PDF-bestanden samenvoegen via een eenvoudige Windows-applicatie.

---

## Lokaal gebruiken

1. Download `Samenvoeger_v*.zip` van de [Releases](../../releases)-pagina.
2. Pak het zip-bestand uit of voer `Samenvoeger_Setup.exe` uit voor een volledige installatie.
3. Start `Samenvoeger.exe`.
4. Selecteer een bronmap of losse PDF-bestanden, kies een doelmap en klik **Start Verwerking**.

### Installatiemodi (Setup.exe)

| Modus | Commando |
|---|---|
| Volledig stil, systeem (Program Files) | `Samenvoeger_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /ALLUSERS` |
| Volledig stil, gebruiker (LocalAppData) | `Samenvoeger_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER` |

---

## Intune deployment

### Win32-app toevoegen

1. Ga naar [Intune-beheercentrum](https://intune.microsoft.com) → **Apps** → **Alle apps** → **Toevoegen**.
2. Kies app-type **Windows-app (Win32)**.
3. Upload `Samenvoeger_v*.intunewin` als app-pakket.

### App-eigenschappen invullen

| Veld | Waarde |
|---|---|
| Naam | Samenvoeger |
| Versie | bijv. `1.2.0` |
| Installatieopdracht | `Samenvoeger_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /ALLUSERS` |
| Verwijderopdracht | `"%ProgramFiles%\Samenvoeger\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART` |
| Installatiegedrag | Systeem |

### Detectieregel instellen

- Type: **Bestand**
- Pad: `%ProgramFiles%\Samenvoeger`
- Bestandsnaam: `Samenvoeger.exe`
- Detectiemethode: Bestand bestaat

### Toewijzing

Wijs de app toe aan de gewenste gebruikers- of apparaatgroep via het tabblad **Toewijzingen**.

---

## Nieuwe versie uitrollen

1. Verhoog het versienummer in `pyproject.toml` én in `installer/samenvoeger.iss`.
2. Commit en tag:
   ```
   git tag v1.x.x && git push origin main v1.x.x
   ```
3. Wacht tot GitHub Actions klaar is — de nieuwe `Samenvoeger_v*.zip` en `Samenvoeger_v*.intunewin` verschijnen automatisch op de Releases-pagina.
4. Ga in Intune naar de app → **Eigenschappen** → upload het nieuwe `.intunewin`-bestand en pas het versienummer aan.
