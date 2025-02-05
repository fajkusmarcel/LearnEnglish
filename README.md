# LearnEnglish

# Nasazeni Flask aplikace pres Apache server

Tento dokument poskytuje kompletní návod pro instalaci Apache, Flask a konfiguraci WSGI pro nasazení jednoduché aplikace Flask na server.

## **1. Instalace Apache a závislostí**

### **Příkazy pro instalaci:**
```bash
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip
```

### **Instalace Flasku:**
```bash
pip3 install flask
```

Pokud máš soubor `requirements.txt`, nainstaluj závislosti:
```bash
pip3 install -r requirements.txt
```

---

## **2. Vytvoření složky pro aplikaci**

Aplikaci ulož do adresáře `/var/www/LearnEnglish/`. Příklad struktury projektu:
```
/var/www/LearnEnglish/
    ├── LearnEnglish.py
    ├── __init__.py
    └── learnenglish.wsgi
```

---

## **3. Vytvoření ukázkové Flask aplikace**

### **Soubor `LearnEnglish.py`:**
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## **4. Vytvoření WSGI souboru**

Vytvoř soubor `/var/www/LearnEnglish/learnenglish.wsgi` s následujícím obsahem:

```python
import sys
import logging

# Nastavení logů
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Přidej cestu k aplikaci
sys.path.insert(0, '/var/www/LearnEnglish')

# Importuj aplikaci
try:
    from LearnEnglish import app as application
except Exception as e:
    logging.exception("Chyba při načítání aplikace")
    raise
```

---

## **5. Konfigurace Apache**

Vytvoř nebo uprav konfigurační soubor Apache:

```bash
sudo nano /etc/apache2/sites-available/learnenglish.conf
```

### **Obsah konfigurace:**
```apache
<VirtualHost *:80>
    ServerName 158.196.109.151  # Nahraď IP adresou nebo doménou

    DocumentRoot /var/www/LearnEnglish

    WSGIDaemonProcess learnenglish python-path=/var/www/LearnEnglish
    WSGIScriptAlias / /var/www/LearnEnglish/learnenglish.wsgi

    <Directory /var/www/LearnEnglish>
        WSGIProcessGroup learnenglish
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/learnenglish_error.log
    CustomLog ${APACHE_LOG_DIR}/learnenglish_access.log combined
</VirtualHost>
```

---

## **6. Nastavení práv k souborům**

Nastav správná práva k souborům aplikace:

```bash
sudo chown -R www-data:www-data /var/www/LearnEnglish
sudo chmod -R 755 /var/www/LearnEnglish
```

---

## **7. Aktivace konfigurace a restart Apache**

### **Aktivace konfigurace:**
```bash
sudo a2ensite learnenglish.conf
```

### **Restart Apache:**
```bash
sudo systemctl restart apache2
```

Pokud je aktivní výchozí konfigurace Apache (`000-default.conf`), deaktivuj ji:
```bash
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
```

---

## **8. Testování aplikace**

Otevři aplikaci v prohlížeči na adrese:
```
http://<IP_adresa_serveru>/
```

Případně spustď test přímo na serveru:
```bash
curl -v http://localhost/
```

Pokud narazíš na chybu **500 Internal Server Error**, zkontroluj logy Apache:
```bash
sudo tail -f /var/log/apache2/learnenglish_error.log
```

---

## **9. Další kroky**

Pokud aplikace funguje, je vhodné:
- Nastavit HTTPS pomocí **Let's Encrypt** a **certbot**:
  ```bash
  sudo apt install certbot python3-certbot-apache
  sudo certbot --apache
  ```
- Optimalizovat konfiguraci pro větší zátěž.

---

Tímto by měla být tvá aplikace plně nasazená a dostupná přes Apache server! 😊

 
