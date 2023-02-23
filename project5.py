import xlsxwriter
import json

workbook = xlsxwriter.Workbook('words_for_years_and_ages.xlsx')

with open('word_data.json', encoding='utf8') as f:
    word_data = json.loads(f.read())

data_ages = {}
data_years = {}
for year in word_data:
    data_years[year] = [0, 0, 0]

for year in word_data:
    for is_comment_group in word_data[year]:
        for word in is_comment_group[0]:
            data_years[year][0] = data_years[year][0] + is_comment_group[0][word]
            data_years[year][2] = data_years[year][2] + is_comment_group[0][word]
        for gender in is_comment_group[1:]:
            for age in gender:
                for word in gender[age]:
                    data_ages[age] = data_ages.get(age, 0) + gender[age][word]
                    data_years[year][1] = data_years[year][1] + gender[age][word]
                    data_years[year][2] = data_years[year][2] + gender[age][word]

worksheet = workbook.add_worksheet()
s = sorted((int(x[0]), x[1]) if x[0] != 'None' else (0, x[1]) for x in data_years.items())
for i in range(len(s)):
    worksheet.write(i, 1, s[i][0])
    worksheet.write(i, 2, s[i][1][0])
    worksheet.write(i, 3, s[i][1][1])
    worksheet.write(i, 4, s[i][1][2])

worksheet = workbook.add_worksheet()
s = sorted((int(x[0]), x[1]) if x[0] != 'None' else (0, x[1]) for x in data_ages.items())
for i in range(len(s)):
    worksheet.write(i, 1, s[i][0])
    worksheet.write(i, 2, s[i][1])
workbook.close()