import requests
import json
import time

TOKEN = '123456'  # пароль

# при запуске №1
users_queue = {(226967859, 2, 17)}
users_for_post = set()
users_finished = set()
groups_queue = set()
groups_finished = set()

# при запуске №2+
with open('users_queue.json') as f:
    users_queue = set([tuple(x) for x in json.loads(f.read())])
with open('users_for_post.json') as f:
    users_for_post = set([tuple(x) for x in json.loads(f.read())])
with open('users_finished.json') as f:
    users_finished = set([tuple(x) for x in json.loads(f.read())])
with open('groups_queue.json') as f:
    groups_queue = set(json.loads(f.read()))
with open('groups_finished.json') as f:
    groups_finished = set(json.loads(f.read()))

 
url = 'https://api.vk.com/method/'
params = {
    'v': '5.131',
    'access_token': TOKEN
}

def get_response(url, f, params):
    response = requests.get(url + f, params=params).json()
    if response.get('error', 0):
        if response['error']['error_code'] != 6:
            return None
        while response.get('error', 0):
            time.sleep(0.2)
            response = requests.get(url + f, params=params).json()
    return response


for step in range(100):
    args = []
    for _ in range(10):
        if not users_queue:
            break
        obj = users_queue.pop()
        users_for_post.add(obj)
        args.append(str(obj[0]))
    params['code'] = '''var a = [''' + ', '.join(['"' + x + '"' for x in args]) + '''];
                        var i = 0;
                        var f = [];
                        var s = [];
                        while (i < 10) {
                            f.push(API.friends.get({'user_id':a[i], 'order':'random', 'fields': 'bdate,sex'}));
                            s.push(API.groups.get({'user_id':a[i]}));
                            i = i + 1;
                        }
                        return [f, s];'''

    response = get_response(url, 'execute', params)
    if response is None:
        continue
    for friends in response['response'][0]:
        if not friends:
            continue
        for friend in friends['items']:
            bdate = None
            if friend.get('bdate'):
                date_split = friend['bdate'].split('.')
                if len(date_split) == 3:
                    bdate = 2022 - int(date_split[2])
            data = (friend['id'], friend['sex'], bdate)
            if friend.get('is_closed', 1):
                if data not in users_queue and data not in users_for_post:
                    users_finished.add(data)
            else:
                if data not in users_for_post and data not in users_finished:
                    users_queue.add(data)

    for groups in response['response'][1]:
        if not groups:
            continue
        for group in groups['items']:
            if group not in groups_finished:
                groups_queue.add(group)

    with open('users_queue.json', 'w') as f:
        f.write(json.dumps(list(users_queue), indent=2))
    with open('users_for_post.json', 'w') as f:
        f.write(json.dumps(list(users_for_post), indent=2))
    with open('users_finished.json', 'w') as f:
        f.write(json.dumps(list(users_finished), indent=2))
    with open('groups_queue.json', 'w') as f:
        f.write(json.dumps(list(groups_queue), indent=2))
    with open('groups_finished.json', 'w') as f:
        f.write(json.dumps(list(groups_finished), indent=2))