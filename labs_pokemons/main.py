import ftplib
import math
import os
import random
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import json
import psycopg2
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Database Connection
conn = psycopg2.connect(
    host="localhost",
    database="Pokemons",
    user="postgres",
    password="4170")

# Send Email Function
def send_email(email, result_battle):
    message = "Бой покемонов"
    try:
        msg = Message(message, sender='',
                      recipients=[email])
        msg.body = result_battle
        mail.send(msg)
        return f"Результат отправлен на почту {email}"
    except Exception as e:
        return "Сообщение не отправилось..."

# Save Recent Pokemon Data to JSON File
def save_most_recent_pokemon(d):
    with open('pokemons.json', 'w') as f:
        json.dump(d, f)

# Load Most Recent Pokemon Data from JSON File
def load_most_recent_pokemon():
    with open('pokemons.json', 'r') as f:
        return json.load(f)

# Check if JSON File is Empty
def is_json_empty():
    file_size = os.path.getsize('pokemons.json')
    if file_size == 0:
        return True
    with open('pokemons.json', 'r') as f:
        d = json.load(f)
        if not d:
            return True
    return False

# Get Pokemon Information from JSON File
def pokemons_info_json(name):
    with open('pokemons.json', 'r') as json_file:
        temp = json.load(json_file)
        for pokemon in temp:
            if pokemon['name'] == name:
                attack = pokemon['attack']
                hp = pokemon['hp']
                img = pokemon['image_url']
    return attack, hp, img

# Get Pokemon Names from API
global names
BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(BASE_URL)
data = response.json()
results = data['results']
names = [pokemon['name'] for pokemon in data['results']]
round_results = []

# Index Route
@app.route('/', methods=['GET'])
def index():
    # Check if JSON File is Empty
    if is_json_empty == True:
        poke = []
        count = 1
        for name in names:
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
            r = requests.get(pokemon_url).json()
            d = {
                'id': r['id'],
                'name': r['name'],
                'speed': r['stats'][-1]['base_stat'],
                'defense': r['stats'][2]['base_stat'],
                'special_defense': r['stats'][4]['base_stat'],
                'attack': r['stats'][1]['base_stat'],
                'special_attack': r['stats'][3]['base_stat'],
                'hp': r['stats'][0]['base_stat'],
                'weight': r['weight'],
                'image_url': r['sprites']['other']['dream_world']['front_default']
            }
            poke.append(d)
            count += 1
        save_most_recent_pokemon(poke)

    # Pagination
    page = request.args.get('page', type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page

    # Search Query
    q = request.args.get('q', '')

    if q:
        pokemons = [pokemon for pokemon in load_most_recent_pokemon() if q.lower() in pokemon['name'].lower()]
    else:
        pokemons = load_most_recent_pokemon()

    total_pages = math.ceil(len(pokemons) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    pokemons = pokemons[start:end]

    return render_template('index.html', pokemons=pokemons, search_query=q,
                           current_page=page, total_pages=total_pages)

@app.route('/fight/<name>', methods=['GET', 'POST'])
def fight(name):
    global attack
    global hp
    global attack_pokemon
    global hp_pokemon
    global opponent_pokemon
    global user_pokemon
    global result
    global img
    global img_pokemon

    if request.method == 'GET':
        opponent_pokemon = random.choice(names).upper()
        attack, hp, img = pokemons_info_json(opponent_pokemon)
        attack_pokemon, hp_pokemon, img_pokemon = pokemons_info_json(name)
        user_pokemon = name
        result = ''
    if request.method == 'POST':
        if hp <= 0 or hp_pokemon <= 0:
            print(hp, hp_pokemon, " sorry")
            result_text = "Игра окончена!"
            if hp < hp_pokemon:
                result = "Вы победили!"
                winner = "Пользователь"
            elif hp > hp_pokemon:
                result = "Вы проиграли..."
                winner = "Враг"
            else:
                result = "Ничья"
                winner = "Ничья"

            return render_template('fight.html', result_text=result_text, opponent_pokemon=opponent_pokemon, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, img=img, img_pokemon=img_pokemon)
        else:
            user_input = int(request.form['submit'])
            opponent_number = random.randint(1, 10)
            print(hp, hp_pokemon)
            if user_input % 2 == opponent_number % 2:
                # отнимаем от жизни оппонента кол-во атак пользовательского покемона
                hp = hp - attack_pokemon
                result_text = "Покемон пользователя наносит удар!"
                if hp <= 0:
                    result = "Вы победили!"
                    winner = "Пользователь"
                    result_text = "Игра окончена!"
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s,%s)",
                        (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                    conn.commit()
            else:
                hp_pokemon = hp_pokemon - attack
                result_text = " Противник бьёт!"
                if hp_pokemon <= 0:
                    result = "Вы проиграли..."
                    winner = "Враг"
                    result_text = "Игра окончена!"
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s,%s)",
                        (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                    conn.commit()
            print(hp, hp_pokemon)
            round_results.append({
                'user_input': user_input,
                'opponent_number': opponent_number,
                'hp': hp,
                'hp_pokemon': hp_pokemon,
                'attack': attack,
                'attack_pokemon': attack_pokemon,
                'result_text': result_text
            })
            return render_template('fight.html', result_text=result_text, 
                                   opponent_pokemon=opponent_pokemon, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, 
                                   img=img, img_pokemon=img_pokemon)

    round_results.clear()  # Очищаем результаты перед началом новой игры
    return render_template('fight.html', opponent_pokemon=opponent_pokemon, 
                           name=name, hp=hp, hp_pokemon=hp_pokemon,
                           result=result, img=img, img_pokemon=img_pokemon)



@app.route('/fight/fast/<name>', methods=['GET', 'POST'])
def quickBattle(name):
    global attack
    global hp
    global attack_pokemon
    global hp_pokemon
    global opponent_pokemon
    global user_pokemon
    global result
    global img
    global img_pokemon
    attack, hp, img = pokemons_info_json(opponent_pokemon)
    attack_pokemon, hp_pokemon, img_pokemon = pokemons_info_json(name)
    user_pokemon = name
    result = ''
    while hp > 0 and hp_pokemon > 0:
        user_input = random.randint(1, 10)
        opponent_number = random.randint(1, 10)
        if user_input % 2 == opponent_number % 2:
            hp = hp - attack_pokemon
            result_text = "Покемон пользователя наносит удар!"
            if hp <= 0:
                result = "Вы победили!"
                winner = "Пользователь"
                result_text = "Игра окончена!"
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s, %s)",
                    (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                conn.commit()
        else:
            hp_pokemon = hp_pokemon - attack
            result_text = " Противник бьёт!"
            if hp_pokemon <= 0:
                result = "Вы проиграли..."
                winner = "Враг"
                result_text = "Игра окончена!"
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s,%s)",
                    (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                conn.commit()

        round_results.append({
            'user_input': user_input,
            'opponent_number': opponent_number,
            'hp': hp,
            'hp_pokemon': hp_pokemon,
            'attack': attack,
            'attack_pokemon': attack_pokemon,
            'result_text': result_text
        })

    result_text = "Игра окончена!"
    if hp < hp_pokemon:
        result = "Вы победили!"
        winner = "Пользователь"
    elif hp > hp_pokemon:
        result = "Вы проиграли..."
        winner = "Враг"
    else:
        result = "Ничья"
        winner = "Ничья"

    if request.method == 'POST':
        if result != "":
            email = request.form.get('email')
            print(email)
            result_text_message = send_email(email, result)

        return render_template('fightFast.html', result_text=result_text,
                               opponent_pokemon=opponent_pokemon,
                               name=name, hp=hp, hp_pokemon=hp_pokemon,
                               result=result, round_results=round_results,
                               img=img, img_pokemon=img_pokemon,
                               result_text_message=result_text_message)

    return render_template('fightFast.html', result_text=result_text,
                           opponent_pokemon=opponent_pokemon,
                           name=name, hp=hp, hp_pokemon=hp_pokemon,
                           result=result, round_results=round_results,
                           img=img, img_pokemon=img_pokemon)


@app.route('/pokemon/<name>', methods=['GET', 'POST'])
def pokemon(name):
    with open('pokemons.json') as json_file:
        d = json.load(json_file)
    # Нахождение покемона по имени в загруженных данных
    pokemon = next((p for p in d if p['name'] == name), None)
    return render_template('pokemonInfo.html', pokemon=pokemon)


@app.route('/pokemon/save/<name>/<speed>/<hp>/<defense>/<attack>/<weight>', methods=['GET', 'POST'])
def save(name, speed, hp, defense, attack, weight):
    USERNAME = ''
    PASSWORD = ''
    HOST = ''
    ftp = ftplib.FTP(HOST, USERNAME, PASSWORD)
    files = ftp.nlst()
    print(files)
    markdown_text = f"# {name}\n\nСкорость: {speed}\n\nЖизнь: {hp}\n\nЗащита: {defense}" \
                    f"\n\nАтака: {attack}\n\nВес: {weight}"
    file_name = f"{name}.md"
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')

    if current_date in ftp.nlst():
        ftp.cwd(current_date)
    else:
        ftp.mkd(current_date)
        ftp.cwd(current_date)

    with open(current_date, 'wb') as f:
        f.write(markdown_text.encode())
    ftp.storbinary('STOR ' + file_name, open(current_date, 'rb'))
    ftp.quit()
    return render_template('savePokemon.html', name=name, speed=speed, hp=hp,
                           defense=defense, attack=attack, weight=weight)


if __name__ == '__main__':
    app.run(port=5000)