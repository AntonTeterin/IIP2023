import json


with open('labels.json', encoding='utf8') as f:
    labels = json.loads(f.read())

scores = {}
for word in labels:
    if labels[word] is None:
        score = 1
    else:
        score = 0
        for label in labels[word]:
            if label is None:
                continue
            if label in ('прост.', 'сниж.', 'презр.', 'уничиж.'):
                score += 0.7
            elif 'жарг.' in label or 'рег.' in label or \
                 label in ('мол.', 'детск.', 'сленг', 'проф.', 'диал.'):
                score += 0.8
            elif label in ('вульг.', 'бран.', 'груб.', 'эвф.'):
                score += 0.9
            elif label in ('табу', 'обсц.'):
                score += 1
        score /= len(labels[word])
    scores[word] = score

with open('scores.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(scores, indent=2, ensure_ascii=False))

