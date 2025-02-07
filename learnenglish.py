from flask import Flask, request, render_template, redirect, url_for, jsonify

import csv
import json
import os
import random

app = Flask(__name__)
# Cesta k aplikaci na serveru 
app.config['APPLICATION_ROOT'] = '/learnenglish'


# Globální proměnné
categories = {
    "nouns": "Podstatná jména",
    "verbs": "Slovesa",
    "phrases": "Fráze",
    "adjectives": "Přídavná jména"  # Nová kategorie
}

words = []
verbs = []



learned_words = set()
wrong_words = []
important_words = []


WRONG_NOUNS_JSON = "wrong_nouns.json"
selected_category = "nouns"  # Výchozí kategorie

# Cesty k souborům
WRONG_ANSWERS_FILE = "dataset/wrong_answers.csv"
NOUN_LEARNED_FILE = "dataset/noun_learned.csv"
NOUN_WRONG_FILE = "dataset/noun_wrong.csv"
NOUN_IMPORTANT_FILE = "dataset/noun_important.csv"

VERBS_LEARNED_FILE = "dataset/verbs_learned.csv"
VERBS_WRONG_FILE = "dataset/verbs_wrong.csv"
VERBS_IMPORTANT_FILE = "dataset/verbs_important.csv"

# ROUTY =========================================================


@app.route('/', methods=['GET', 'POST'])
def index():
    global selected_category

    # Zpracování formuláře při POST požadavku
    if request.method == 'POST':
        selected_category = request.form.get('category', 'nouns')

    # Pokud kategorie není nastavena, použijeme výchozí hodnotu
    if not selected_category:
        selected_category = 'nouns'

    load_noun(selected_category)
    load_learned_words(selected_category)
    load_wrong_words(selected_category)
    load_important_words(selected_category)

    total_words = len(words)
    learned_count = len(learned_words)
    wrong_count = len(wrong_words)
    important_count = len(important_words)

    return render_template(
        'index.html',
        categories=categories,
        selected_category=selected_category,
        total_words=total_words,
        learned_count=learned_count,
        wrong_count=wrong_count,
        important_count=important_count
    )


@app.route('/start_test', methods=['POST'])
def start_test():
    category = request.form.get('category', 'nouns')
    num_words = int(request.form.get('num_words', 10))
    
    load_learned_words(category)
    load_wrong_words(category)
    load_important_words(category)

    if category == "verbs":
        load_verbs(category)    
        if not verbs:
            return render_template('result.html', message="---Nejsou dostupná žádná slovesa k procvičení.")

        selected_tenses = request.form.getlist('tense')
        if not selected_tenses:
            return render_template('result.html', message="Nejsou vybrány žádné časové tvary k procvičení.")

        # Výběr sloves a náhodných tvarů
        selected_verbs = random.sample(verbs, min(num_words, len(verbs)))
        questions = []
        for verb in selected_verbs:
            tense = random.choice(selected_tenses)
            questions.append({
                "word": verb["word"],
                "tense": tense,
                "correct_answer": verb[tense]
            })

        print(f"Zvolené časové tvary: {selected_tenses}")
        print(f"Počet sloves načtených ze souboru: {len(verbs)}")

        return render_template('verbs_test.html', questions=questions)
    else:
        load_noun(category)
        if not words:
            return render_template('result.html', message="Nejsou dostupná žádná slova k procvičení.")

        test_words = select_test_words(num_words, category)
        return render_template('test.html', words=test_words)

@app.route('/start_wrong_test', methods=['POST'])
def start_wrong_test():
    category = request.form.get('category', 'nouns')
    num_words = int(request.form.get('num_words', 10))

    # Načtení dat a špatně zodpovězených slov podle kategorie
    if category == "verbs":
        load_verbs(category)
        load_wrong_words(category)
        available_wrong_words = [verb for verb in verbs if verb["word"] in wrong_words]
    else:
        load_noun(category)
        load_wrong_words(category)
        available_wrong_words = [word for word in words if word[0] in wrong_words]

    # Kontrola dostupnosti špatně zodpovězených slov
    if not available_wrong_words:
        return render_template('result.html', message="Nejsou žádná špatně zodpovězená slova k procvičení.")

    # Výběr náhodných špatně zodpovězených slov
    num_words_to_test = min(num_words, len(available_wrong_words))
    selected_words = random.sample(available_wrong_words, num_words_to_test)

    # Speciální zpracování pro slovesa
    if category == "verbs":
        selected_tenses = request.form.getlist('tense')
        if not selected_tenses:
            return render_template('result.html', message="Nejsou vybrány žádné časové tvary k procvičení.")

        # Vytvoření otázek pro slovesa
        questions = []
        for verb in selected_words:
            tense = random.choice(selected_tenses)
            questions.append({
                "word": verb["word"],
                "tense": tense,
                "correct_answer": verb[tense]
            })

        return render_template('verbs_test.html', questions=questions)

    # Zpracování pro podstatná jména
    return render_template('test.html', words=selected_words)



@app.route('/submit_test', methods=['POST'])
def submit_test():
    category = request.form.get('category', 'nouns')
    load_wrong_words(category)

    results = []

    # Zpracování odpovědí
    for key in request.form.keys():
        if key.startswith("test_word_"):
            word_data = request.form[key].split(";")
            word_text = word_data[0]
            correct_answer = word_data[1]
            user_input = request.form.get(f"answer_{word_text}", "").strip()

            if user_input.lower() == correct_answer.lower():
                # Správná odpověď
                if word_text in wrong_words:
                    wrong_words.remove(word_text)
                learned_words.add(word_text)
                result = {"word": word_text, "correct_answer": correct_answer, "status": "Správně", "user_input":user_input}
            else:
                # Špatná odpověď
                if word_text not in wrong_words:
                    wrong_words.append(word_text)
                result = {"word": word_text, "correct_answer": correct_answer, "status": "Špatně", "user_input":user_input}

            results.append(result)

    # Uložení výsledků
    save_wrong_words(category)
    save_learned_words(category)

    return render_template('result.html', results=results)

@app.route('/submit_verbs_test', methods=['POST'])
def submit_verbs_test():
    category = request.form.get('category', 'verbs')
    load_wrong_words(category)
    load_learned_words(category)

    results = []

    # Zpracování odpovědí
    for key in request.form.keys():
        if key.startswith("test_word_"):
            word_data = request.form[key].split(";")
            word = word_data[0]  # Český výraz
            tense = word_data[1]  # Časový tvar
            correct_answer = word_data[2]  # Správný překlad

            user_input = request.form.get(f"answer_{word}", "").strip()

            if user_input.lower() == correct_answer.lower():
                # Správná odpověď
                if word in wrong_words:
                    wrong_words.remove(word)
                learned_words.add(word)
                result = {"word": word, "tense": tense, "user_input": user_input, "correct_answer": correct_answer, "status": "Správně"}
            else:
                # Špatná odpověď
                if word not in wrong_words:
                    wrong_words.append(word)
                result = {"word": word, "tense": tense, "user_input": user_input, "correct_answer": correct_answer, "status": "Špatně"}

            results.append(result)

    # Uložení výsledků
    save_wrong_words(category)
    save_learned_words(category)

    return render_template('result.html', results=results)

@app.route('/view_wrong_words', methods=['POST'])
def view_wrong_words():
    category = request.form.get('category', 'nouns')
    load_wrong_words(category)

    if not wrong_words:
        return render_template('result.html', message="Nejsou žádná špatně zodpovězená slova k zobrazení.")

    # Připravit data pro zobrazení
    words_data = []
    if category == "verbs":
        load_verbs(category)
        words_data = [verb for verb in verbs if verb["word"] in wrong_words]
    else:
        load_noun(category)
        words_data = [word for word in words if word[0] in wrong_words]

    return render_template('wrong_words.html', words=words_data, selected_category=category)


@app.route('/view_important_words', methods=['POST'])
def view_important_words():
    category = request.form.get('category', 'nouns')
    load_important_words(category)

    if not important_words:
        return render_template('result.html', message="Nejsou žádná špatně zodpovězená slova k zobrazení.")

    important_word_list = [w["word"] for w in important_words]

    # Připravit data pro zobrazení    
    words_data = []
    if category == "verbs":
        load_verbs(category)
        words_data = [verb for verb in verbs if verb["word"] in important_word_list]
    else:
        load_noun(category)
        words_data = [word for word in words if word[0] in important_word_list]        

    return render_template('important_words.html', words=words_data, selected_category=category)

@app.route('/save_important_word', methods=['POST'])
def save_important_word():
    data = request.get_json()
    category = selected_category
    word = data.get('word')
    correct_answer = data.get('correct_answer')

    # Cesta k souboru
    base_dir = os.path.dirname(os.path.abspath(__file__))
    important_filename = os.ghpath.join(base_dir, 'dataset', f'{category}_important.json')

    #important_filename = f"dataset/{category}_important.json"

    # Načtení existujících dat
    if os.path.exists(important_filename):
        with open(important_filename, 'r', encoding='utf-8') as file:
            important_words = json.load(file)
    else:
        important_words = []

    # Přidání nového slova, pokud ještě není uloženo
    if not any(w["word"] == word for w in important_words):
        important_words.append({"word": word, "correct_answer": correct_answer})

        # Uložení do souboru
        with open(important_filename, 'w', encoding='utf-8') as file:
            json.dump(important_words, file, ensure_ascii=False, indent=4)

    return jsonify({"success": True})

#PODSTATNA JMENA ================================================
def load_noun(category):
    global words
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(base_dir, 'dataset', f'{category}.csv')
    #filename = f"dataset/{category}.csv"
    words = []
    try:
        with open(filename, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                words.append(row)
        print(f"Načteno {len(words)} slov ze souboru {filename}")
    except FileNotFoundError:
        print(f"Soubor {filename} nebyl nalezen.")

def select_test_words(num_words, category):
    load_noun(category)
    load_wrong_words(category)

    # Výběr špatně zodpovězených slov
    num_wrong = min(max(1, num_words // 5), len(wrong_words))
    wrong_sample = random.sample(
        [word for word in words if word[0] in wrong_words], 
        min(num_wrong, len(wrong_words))
    )

    # Výběr zbývajících slov
    remaining_words = [word for word in words if word[0] not in wrong_words]
    remaining_count = num_words - len(wrong_sample)

    normal_sample = random.sample(remaining_words, min(remaining_count, len(remaining_words))) if remaining_count > 0 else []

    return wrong_sample + normal_sample



# SLOVESA =======================================================

# PODPURNE ======================================================

# Funkce pro získání názvů souborů na základě kategorie
def get_json_filenames(category):
    
    base_dir = os.path.dirname(os.path.abspath(__file__))

    learned_file = os.path.join(base_dir, 'dataset', f'{category}_learned.json')
    wrong_file = os.path.join(base_dir, 'dataset', f'{category}_wrong.json')
    important_file = os.path.join(base_dir, 'dataset', f'{category}_important.json')

    return learned_file, wrong_file, important_file

    #return f"dataset/{category}_learned.json", f"dataset/{category}_wrong.json", f"dataset/{category}_important.json"

# Načtení naučených slov pro danou kategorii
def load_learned_words(category):
    global learned_words
    learned_words = set()
    learned_filename = get_json_filenames(category)[0]
    if os.path.exists(learned_filename):
        with open(learned_filename, 'r', encoding='utf-8') as file:
            learned_words = set(json.load(file))

# Načtení chybně zodpovězených slov pro danou kategorii
def load_wrong_words(category):
    global wrong_words
    wrong_words = []
    wrong_filename = get_json_filenames(category)[1]
    if os.path.exists(wrong_filename):
        with open(wrong_filename, 'r', encoding='utf-8') as file:
            wrong_words = json.load(file)

# Načtení dulezitych slov pro danou kategorii
def load_important_words(category):
    global important_words
    important_words = []
    important_filename = get_json_filenames(category)[2]
    print("  Nacitam important")
    print(important_filename)

    if os.path.exists(important_filename):
        with open(important_filename, 'r', encoding='utf-8') as file:
            important_words = json.load(file)

# Uložení naučených slov pro danou kategorii
def save_learned_words(category):
    learned_filename = get_json_filenames(category)[0]
    with open(learned_filename, 'w', encoding='utf-8') as file:
        json.dump(list(learned_words), file, ensure_ascii=False, indent=4)

# Uložení chybně zodpovězených slov pro danou kategorii
def save_wrong_words(category):
    wrong_filename = get_json_filenames(category)[1]
    with open(wrong_filename, 'w', encoding='utf-8') as file:
        json.dump(wrong_words, file, ensure_ascii=False, indent=4)

# Uložení dulezitych slov pro danou kategorii
def save_important_words(category):
    important_filename = get_json_filenames(category)[2]
    with open(important_filename, 'w', encoding='utf-8') as file:
        json.dump(important_filename, file, ensure_ascii=False, indent=4)

import json
import os



# VERBS
def load_verbs(category):
    global verbs
    verbs = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.ghpath.join(base_dir, 'dataset', f'{category}.csv')
    #filename = f"dataset/{category}.csv"
    try:
        with open(filename, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                # Přeskočíme prázdné řádky nebo řádky s nesprávným počtem sloupců
                if not row or len(row) != 6:
                    continue

                # Přidáme slovo do seznamu
                verbs.append({
                    "word": row[0],
                    "present": row[1],
                    "present_continuous": row[2],
                    "past": row[3],
                    "past_continuous": row[4],
                    "future": row[5]
                })
        print(f"Načteno {len(verbs)} sloves ze souboru verbs.csv")
    except FileNotFoundError:
        print("Soubor verbs.csv nebyl nalezen.")
    except Exception as e:
        print(f"Chyba při načítání souboru: {e}")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
