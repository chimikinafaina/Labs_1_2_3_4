import datetime
import ftplib
import markdown
import redis
import json
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests


def save_pokemon_info(name):
    USERNAME = ''
    PASSWORD = ''
    PORT = 21

    ftp = ftplib.FTP('', USERNAME, PASSWORD)

    files = ftp.nlst()
    print(files)

    markdown_text = f"# {name}\n"
    html_text = markdown.markdown(markdown_text)

    file_name = f"{name}.md"
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    file_path = f"{current_date}/{file_name}"

    if current_date in ftp.nlst():
        ftp.cwd(current_date)
    else:
        ftp.mkd(current_date)
        ftp.cwd(current_date)

    with open(current_date, 'wb') as f:
        f.write(markdown_text.encode())
    ftp.storbinary('STOR ' + file_name, open(current_date, 'rb'))

    ftp.quit()


def save_most_recent_pokemon(pokemon):
    redis_client.set(pokemon['name'], json.dumps(pokemon))


def load_most_recent_pokemon(name):
    data = redis_client.get(name)
    if data:
        return json.loads(data)
    else:
        return None


def delete_pokemon_data(name):
    redis_client.delete(name)
    print(f"{name} успешно удален")


def index(name):
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(BASE_URL)
    data = response.json()
    names = [pokemon['name'] for pokemon in data['results']]
    poke = []
    count = 1
    pokemon = load_most_recent_pokemon(name)
    if not pokemon:
        pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
        r = requests.get(pokemon_url).json()
        pokemon = {
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
        save_most_recent_pokemon(pokemon)
    poke.append(pokemon)
    count += 1
    print('Завершилось!')
    # for name in names:
    #     pokemon = load_most_recent_pokemon(name)
    #     if not pokemon:
    #         pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    #         r = requests.get(pokemon_url).json()
    #         pokemon = {
    #             'id': r['id'],
    #             'name': r['name'],
    #             'speed': r['stats'][-1]['base_stat'],
    #             'defense': r['stats'][2]['base_stat'],
    #             'special_defense': r['stats'][4]['base_stat'],
    #             'attack': r['stats'][1]['base_stat'],
    #             'special_attack': r['stats'][3]['base_stat'],
    #             'hp': r['stats'][0]['base_stat'],
    #             'weight': r['weight'],
    #             'image_url': r['sprites']['other']['dream_world']['front_default']
    #         }
    #         save_most_recent_pokemon(pokemon)
    #     poke.append(pokemon)
    #     count += 1


if __name__ == '__main__':
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8")

    try:
        response = redis_client.ping()
        if response:
            print('Есть соединение с Redis')
            name = 'BULBASAUR'
            #index(name)
            print(load_most_recent_pokemon(name))
            #delete_pokemon_data(name)
    except redis.ConnectionError:
        print('Нет соединения с Redis')
