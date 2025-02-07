# LearnEnglish

# Nasazeni Flask aplikace pres Apache server

Tento návod poskytuje kompletní návod pro instalaci Apache, Flask a konfiguraci WSGI pro nasazení jednoduché aplikace Flask na server.

## **1. Instalace Apache a závislostí**

```bash
sudo apt update
sudo apt-get install apache2 libapache2-mod-wsgi-py3 python3-pip python3-venv
```

---

## **2. Práva přístupu**
Nastavení vlastnictví a práv na adresář /var/www.

```bash
sudo chown -R www-data:www-data /var/www
sudo chmod -R 775 /var/www
```

Přidání uživatele franta do skupiny www-data
```bash
sudo usermod -a -G www-data franta
```

Nastavení dědičnosti práv pro skupinu
```bash
sudo chmod g+s /var/www
```

---


## **3. Vytvoření složky pro aplikaci**

Aplikaci ulož do adresáře `/var/www/LearnEnglish/`. Příklad struktury projektu:
```
/var/www/LearnEnglish/
    ├── learnenglish.py
    └── learnenglish.wsgi
```

---

## **4. Vytvoření a aktivace virtuálního prostředí**
```python
cd /var/www/LearnEnglish
python3 -m venv venv
source venv/bin/activate
pip install flask
# Po instalaci potřebných balíčků se můžeš odpojit:
deactivate
```
---

## **5. Vytvoření ukázkové Flask aplikace**

### **Soubor `learnenglish.py`:**
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
```
> [!TIP]
> Případně si stáhněte aplikaci LearnEnglish z GitHUB pomocí příkazu. Více informací ohledně nastavení ssh, viz bod 12.
```bash
git clone git@github.com:fajkusmarcel/LearnEnglish.git
```

---

## **6. Vytvoření WSGI souboru**

Vytvoř soubor `/var/www/LearnEnglish/learnenglish.wsgi` s následujícím obsahem:

```python
import sys
import os

# Cesta k aplikaci
sys.path.insert(0, '/var/www/LearnEnglish')
# Importuj aplikaci
try:
    from learnenglish import app as application
except Exception as e:
    logging.exception("Chyba při načítání aplikace")
    raise
```

---

## **7. Konfigurace Apache**

Vytvoř konfigurační soubor Apache:

```bash
sudo nano /etc/apache2/sites-available/learnenglish.conf
```

### **Obsah konfigurace:**
```apache
<VirtualHost *:80>
    ServerName 158.196.109.151

    # FlaskApp1
    WSGIDaemonProcess learnenglish python-path=/var/www/LearnEnglish python-home=/var/www/LearnEnglish/venv
    WSGIScriptAlias /learnenglish /var/www/LearnEnglish/learnenglish.wsgi

    <Directory /var/www/LearnEnglish>
        Require all granted
    </Directory>

    # Dalsi aplikace, napr. FlaskApp
    WSGIDaemonProcess flaskapp python-path=/var/www/FlaskApp python-home=/var/www/FlaskApp/venv
    WSGIScriptAlias /flaskapp /var/www/FlaskApp/flaskapp.wsgi

    <Directory /var/www/FlaskApp>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/flaskapps-error.log
    CustomLog ${APACHE_LOG_DIR}/flaskapps-access.log combined
</VirtualHost>
```

---

## **8. Nastavení práv k souborům**

Nastav správná práva k souborům aplikace:

```bash
sudo chown -R www-data:www-data /var/www/LearnEnglish
sudo chmod -R 755 /var/www/LearnEnglish
```
Přidání uživatele do skupiny www-data
```bash
sudo usermod -a -G www-data fajkus
```


---

## **9. Aktivace konfigurace a restart Apache**

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

## **10. Testování aplikace**

Otevři aplikaci v prohlížeči na adrese:
```
http://<IP_adresa_serveru>/helloworld
```

Případně spustď test přímo na serveru:
```bash
curl -v http://localhost/helloworld
```

Pokud narazíš na chybu **500 Internal Server Error**, zkontroluj logy Apache:
```bash
sudo tail -f /var/log/apache2/helloworldflaskapache_error.log
```

---

## **11. Další kroky**

Pokud aplikace funguje, je vhodné:
- Nastavit HTTPS pomocí **Let's Encrypt** a **certbot**:
  ```bash
  sudo apt install certbot python3-certbot-apache
  sudo certbot --apache
  ```
- Optimalizovat konfiguraci pro větší zátěž.

---

## **12. Nastavení SSH klíče pro přístup k repozitáři**

### 1. **Vytvoření SSH klíče**
Vytvoř SSH klíč jako běžný uživatel (např. `franta`) pomocí následujícího příkazu:

```bash
ssh-keygen -t ed25519 -C "fajkusmarcel@gmail.com"
```

- Potvrď uložení do výchozího adresáře (`~/.ssh/id_ed25519`) stisknutím **Enter**.
- Pokud chceš zabezpečit klíč heslem, zadej jej (jinak můžeš stisknout **Enter**).

### 2. **Přidání klíče do SSH agenta**
Pro snazší používání přidej privátní klíč do SSH agenta. Nejprve zkontroluj, zda agent běží:

```bash
eval "$(ssh-agent -s)"
```

Pokud se agent spustí, přidej do něj klíč:

```bash
ssh-add ~/.ssh/id_ed25519
```

Ověř, že klíč byl přidán správně:

```bash
ssh-add -l
```

### 3. **Otestování připojení k repozitáři**
Otestuj připojení k GitHubu pomocí příkazu:

```bash
ssh -T git@github.com
```

Pokud je vše v pořádku, měl by se zobrazit výstup potvrzující úspěšnou autentizaci.

### 4. **Stažení repozitáře**
Nyní můžeš klonovat repozitář pomocí SSH URL:

```bash
git clone git@github.com:fajkusmarcel/LearnEnglish.git
```

Tento příkaz stáhne obsah repozitáře `LearnEnglish` do aktuálního adresáře.

