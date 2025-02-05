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