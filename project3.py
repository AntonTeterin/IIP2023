from bs4 import BeautifulSoup
import requests
import json

with open('word_data.json', encoding='utf8') as f:
    word_data = json.loads(f.read())

# при запуске №1
# labels = {}

# при запуске №2+
with open('labels.json', encoding='utf8') as f:
    labels = json.loads(f.read())

data = {}

for year in word_data:
    for is_comment_group in word_data[year]:
        for word in is_comment_group[0]:
            data[word] = data.get(word, 0) + is_comment_group[0][word]
        for gender in is_comment_group[1:]:
            for age in gender:
                for word in gender[age]:
                    data[word] = data.get(word, 0) + gender[age][word]


words_list = sorted(data.items(), key=lambda x: x[1], reverse=True)
count = 0

for word, _ in words_list:
    count += 1
    if count > 100000:
        break
    # для нарицательных слов
    if word in labels:
        continue
    response = requests.get('https://ru.wiktionary.org/wiki/' + word)

    # для имен собственных
    if labels[word] is not None:
        continue
    response = requests.get('https://ru.wiktionary.org/wiki/' + word.title())
    # для аббревиатур
    response = requests.get('https://ru.wiktionary.org/wiki/' + word.upper())

    soup = BeautifulSoup(response.content, 'lxml')

    res = soup.find("div", id="mw-content-text").find('ol')
    if res is None:
        labels[word] = None
    else:
        labels[word] = []
        for x in res.children:
            if x.name is not None:
                r = x.find("a", title="Викисловарь:Условные сокращения")
                label = None
                if r is not None:
                    r = r.span
                    if r is not None:
                        label = r.text
                labels[word].append(label)
    if not count % 100:
        with open('labels.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(labels, indent=2, ensure_ascii=False))
