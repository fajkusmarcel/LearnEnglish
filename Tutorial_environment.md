# Práce s virtuálním prostředím v Pythonu

Tento dokument popisuje, jak vytvořit, spravovat a používat virtuální prostředí v Pythonu. Virtuální prostředí slouží k izolaci závislostí jednotlivých projektů a zamezení konfliktům mezi verzemi knihoven.

---

## **1. Vytvoření virtuálního prostředí**

Přejdi do složky, kde chceš uložit svůj projekt, a vytvoř virtuální prostředí:

```bash
python3 -m venv venv
```

Tento příkaz vytvoří složku `venv`, která obsahuje izolovanou kopii Pythonu a prostor pro knihovny.

---

## **2. Aktivace virtuálního prostředí**

Před prácí s projektem je třeba aktivovat virtuální prostředí.

### **Na Linuxu nebo macOS:**
```bash
source venv/bin/activate
```

### **Na Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

Po aktivaci by se měla zobrazit informace o aktivním prostředí, např. `(venv)` v příkazu terminálu.

---

## **3. Instalace knihoven**

Po aktivaci můžeš instalovat knihovny pomocí `pip`. Tyto knihovny budou dostupné pouze v tomto prostředí.

Například instalace Flasku:
```bash
pip install flask
```

Závislosti projektu lze uložit do souboru `requirements.txt`:
```bash
pip freeze > requirements.txt
```

Tento soubor lze později použít pro instalaci všech závislostí na jiném stroji nebo prostředí:
```bash
pip install -r requirements.txt
```

---

## **4. Deaktivace virtuálního prostředí**

Po skončení práce můžeš deaktivovat virtuální prostředí:

```bash
deactivate
```

Po deaktivaci se terminál vrátí zpět do systémového prostředí.

---

## **5. Použití virtuálního prostředí s Apache (mod_wsgi)**

Pokud nasazuješ aplikaci na server s Apache a `mod_wsgi`, je třeba specifikovat cestu k virtuálnímu prostředí v konfiguraci Apache.

### **Ukázka konfigurace:**
```apache
<VirtualHost *:80>
    ServerName example.com

    # Definuj WSGI proces s cestou k virtuálnímu prostředí
    WSGIDaemonProcess myapp python-path=/var/www/MyApp python-home=/var/www/MyApp/venv
    WSGIScriptAlias / /var/www/MyApp/myapp.wsgi

    <Directory /var/www/MyApp>
        Require all granted
        WSGIProcessGroup myapp
        WSGIApplicationGroup %{GLOBAL}
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/myapp-error.log
    CustomLog ${APACHE_LOG_DIR}/myapp-access.log combined
</VirtualHost>
```

---

## **6. Odstranění virtuálního prostředí**

Pokud již prostředí nepotřebuješ, můžeš jej jednoduše smazat:

```bash
rm -rf venv
```

---

## **7. Tipy a triky**

- **Kontrola nainstalovaných knihoven:**
  ```bash
  pip list
  ```

- **Aktualizace knihoven:**
  ```bash
  pip install --upgrade <nazev_knihovny>
  ```

- **Zobrazení nápovědy:**
  ```bash
  pip --help
  ```

---

Tímto způsobem můžeš efektivně spravovat závislosti a izolaci Python projektů na jednom serveru. 😊
