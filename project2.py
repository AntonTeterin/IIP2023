import requests
import json
import time
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
TOKEN = '123456'  # пароль

# при запуске №1
word_data = {}
for x in range(2006, 2024):
    word_data[str(x)] = [[{}, {}, {}], [{}, {}, {}]]
counts = []

# при запуске №2+
with open('groups_queue.json') as f:
    groups_queue = set(json.loads(f.read()))
with open('groups_finished.json') as f:
    groups_finished = set(json.loads(f.read()))
with open('counts.json') as f:
    counts = [tuple(x) for x in json.loads(f.read())]
with open('word_data.json', encoding='utf8') as f:
    word_data = json.loads(f.read())


def get_year(date):
    return date // 31557600 + 1970

def get_response(url, f, params):
    response = requests.get(url + f, params=params).json()
    if response.get('error', 0):
        if response['error']['error_code'] != 6:
            return None
        while response.get('error', 0):
            time.sleep(0.3)
            response = requests.get(url + f, params=params).json()
    return response

def get_data(year, is_comment, gender, age, text):
    global all_count
    all_count += 1
    year, age = str(year), str(age)
    dictionary = word_data[year][is_comment][gender]
    if gender:
        dictionary[age] = dictionary.get(age, {})
        dictionary = dictionary[age]
    word = ''
    for sym in text.lower():
        if 1071 < ord(sym) < 1104 or ord(sym) == 1105:
            word += sym
        elif word:
            res = morph.parse(word)[0].normal_form
            dictionary[res] = dictionary.get(res, 0) + 1
            word = ''

def get_comments(post_id, count):
    params_com['post_id'] = post_id
    params_com['offset'] = 0
    while params_com['offset'] < count:
        response = get_response(url, 'wall.getComments', params_com)
        if response is None:
            return
        users = {}
        for user in response['response']['profiles']:
            bdate = None
            if user.get('bdate'):
                x = user['bdate'].split('.')
                if len(x) == 3:
                    bdate = 2022 - int(x[2])
            users[user['id']] = (user['sex'], bdate)
        for comm in response['response']['items']:
            from_id = comm['from_id']
            if from_id > 0:
                gender, age = users[comm['from_id']]
            else:
                gender, age = 0, None
            get_data(get_year(comm['date']), 1, gender, age, comm['text'])
            for comm2 in comm['thread']['items']:
                from_id = comm2['from_id']
                if from_id > 0:
                    gender, age = users[comm2['from_id']]
                else:
                    gender, age = 0, None
                get_data(get_year(comm2['date']), 1, gender, age, comm2['text'])

        params_com['offset'] = params_com['offset'] + 100


url = 'https://api.vk.com/method/'
params = {
    'v': '5.131',
    'access_token': TOKEN,
    'count': 100,
    'offset': 0
}

params_com = {
    'v': '5.131',
    'access_token': TOKEN,
    'count': 100,
    'offset': 0,
    'extended': 1,
    'fields': 'bdate,sex',
    'thread_items_count': 10
}

for step in range(100):
    for i in range(5):
        obj_id = groups_queue.pop()
        groups_finished.add(obj_id)
        params['owner_id'] = params_com['owner_id'] = -obj_id
        params['offset'] = 0
        count = 100
        all_count = 0
        comm_count = 0

        response = get_response(url, 'wall.get', params)
        if response is None:
            continue
        for post in response['response']['items']:
            get_data(get_year(post['date']), 0, 0, None, post['text'])
            get_comments(post['id'], post['comments']['count'])
            comm_count += post['comments']['count']

        while count < min(response['response']['count'], 1000):
            params['offset'] = count
            count += 100
            response = get_response(url, 'wall.get', params)
            if response is None:
                continue
            for post in response['response']['items']:
                get_data(get_year(post['date']), 0, 0, None, post['text'])
                get_comments(post['id'], post['comments']['count'])
                comm_count += post['comments']['count']
        counts.append((obj_id, min(response['response']['count'], 1000),
                       response['response']['count'], all_count, comm_count))

    with open('groups_queue.json', 'w') as f:
        f.write(json.dumps(list(groups_queue), indent=2))
    with open('groups_finished.json', 'w') as f:
        f.write(json.dumps(list(groups_finished), indent=2))
    with open('word_data.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(word_data, indent=2, ensure_ascii=False))
    with open('counts.json', 'w') as f:
        f.write(json.dumps(counts, indent=2))
