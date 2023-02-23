import xlsxwriter
import json


with open('scores.json', encoding='utf8') as f:
    scores = json.loads(f.read())

with open('word_data.json', encoding='utf8') as f:
    word_data = json.loads(f.read())

workbook = xlsxwriter.Workbook('the_end_result.xlsx')

for is_comment_range, gender_range, name_worksheet in (([0], [0, 1, 2], 'Все посты'),
                                                 ([1], [1], 'Жен комм'),
                                                 ([1], [2], 'Муж комм'),
                                                 ([1], [0, 1, 2], 'Все комм'),
                                                 ([0, 1], [0, 1, 2], 'Всё')):

    worksheet_score = workbook.add_worksheet(name_worksheet + '- Загрязнение')
    worksheet_lexicon = workbook.add_worksheet(name_worksheet + '- Словарный запас')

    year_ranges = (list(range(2006, 2024)), *[[year] for year in range(2006, 2024)])
    age_ranges = (list(range(14, 74)), *[[a, a + 1, a + 2] for a in range(14, 74, 3)])
    for i in range(len(year_ranges)):
        worksheet_lexicon.write(0, i + 1, str(year_ranges[i]))
        worksheet_score.write(0, i + 1, str(year_ranges[i]))
        for j in range(len(age_ranges)):
            if not i:
                worksheet_lexicon.write(j + 1, 0, str(age_ranges[j]))
                worksheet_score.write(j + 1, 0, str(age_ranges[j]))
            data = {}
            for year in year_ranges[i]:
                year = str(year)
                for is_comment_group_id in is_comment_range:
                    is_comment_group = word_data[year][is_comment_group_id]
                    for gender_id in gender_range:
                        gender_group = is_comment_group[gender_id]
                        if gender_id:
                            for age in age_ranges[j]:
                                age = str(age)
                                for word in gender_group.get(age, {}):
                                    data[word] = data.get(word, 0) + gender_group[age][word]
                        else:
                            for word in gender_group:
                                data[word] = data.get(word, 0) + gender_group[word]
            score = 0
            count = 0
            lexicon = 0
            for word in data:
                res = scores.get(word, None)
                if res is None:
                    continue
                score += data[word] * scores[word]
                count += data[word]
                lexicon += 1
            if count:
                worksheet_score.write(j + 1, i + 1, float(f'{score * 1000 / count:.3f}'))
            else:
                worksheet_score.write(j + 1, i + 1, '-')
            worksheet_lexicon.write(j + 1, i + 1, lexicon)
workbook.close()