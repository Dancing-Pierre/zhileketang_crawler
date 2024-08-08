# -*- coding: utf-8 -*-
import json
import re
import time

import pandas as pd
import requests


def remove_span_tags(text):
    return re.sub(r'<span[^>]*>(.*?)<\/span>', r'\1', text)


def get_img(text):
    """
    下载图片
    :param text:
    :return:
    """
    img_src_list = []
    if text:
        img_src_list.extend(re.findall(r'<img\s+src="([^"]+)"', text))
        if img_src_list:
            for i in range(0, len(img_src_list)):
                url = img_src_list[i]
                file_name = url.split('/')[-1]
                new_file_name = '/public/images/' + file_name
                if 'https://' in url:
                    img_url = url
                else:
                    img_url = 'https://image.zlketang.com' + url
                r = requests.get(img_url)
                with open(file_name, "wb") as f:  # wb是写二进制
                    f.write(r.content)
                text = text.replace(url, new_file_name)
                time.sleep(1)
    return text


def replace_empty_list(option):
    if '[' in option and ']' in option:
        for i in eval(option):
            if not i:
                return None
            else:
                return option
    else:
        return option


with open('第九节 主要合同.json', 'r', encoding='utf-8') as file:
    response = json.load(file)
exam_name = str(response['data']['exam_name']).replace('\t', '').replace('\n', '').strip()

data = []
print(exam_name)
detail = response['data']['parts']
# 类型：选择、填空、判断
for per_part in detail:
    part_title = per_part['title']
    if part_title == '不定项选择题':
        part_title = '多项选择题'
    questions = per_part['questions']
    for question in questions:
        data_dict = {}
        question_title = question['description']
        # 提取图片
        question_title = get_img(question_title)
        data_dict['题目'] = question_title.replace('&nbsp;', ' ')
        options = question['options']
        options = json.loads(options)
        if any(keyword in part_title for keyword in ['综合题', '计算分析题', '简答题', '案例分析']):
            all_options = []
            if type(options) == list:
                for per_trouble in options:
                    tmp_title = data_dict['题目'] + per_trouble['description'].replace('&nbsp;',
                                                                                       ' ')
                    tmp_title = get_img(tmp_title)
                    all_options.append(tmp_title)
            answer = question['answer']
            all_answers = []
            try:
                if type(eval(answer)) == list:
                    answers = json.loads(answer)
                    for answer in answers:
                        answer = answer.replace('&nbsp;', ' ')
                        answer = get_img(answer)
                        all_answers.append(answer)
            except:
                all_answers = [answer]
            solution = question['solution']
            all_solutions = []
            try:
                if type(eval(solution)) == list:
                    solutions = json.loads(solution)
                    for solution in solutions:
                        solution = solution.replace('&nbsp;', ' ')
                        solution = get_img(solution)
                        all_solutions.append(solution)
            except:
                all_solutions = [solution]
            zipped = zip(all_options, all_answers, all_solutions)
            for per_zip in list(zipped):
                data_dict = {'题目类型': part_title, '题目': per_zip[0], 'answer': per_zip[1],
                             'solution': per_zip[2]}
                data.append(data_dict)
        elif '计算题' in part_title:
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            if options:
                # 输出结果
                solutions = eval(solutions.replace('&nbsp;', ' '))
                for i in range(0, options_num):
                    data_dict = {}
                    data_dict['题目类型'] = part_title
                    title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                    option = options[i]['options']
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
                    title = get_img(title)
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '').replace('&nbsp;', ' ')
                    answer = get_img(answer)
                    data_dict['answer'] = answer
                    solution = get_img(solutions[i])
                    data_dict['solution'] = solution
                    data.append(data_dict)
            else:
                data_dict['题目类型'] = part_title
                question_title = get_img(question_title)
                data_dict['题目'] = question_title
                answers = get_img(answers)
                data_dict['answer'] = answers
                solutions = solutions.replace('&nbsp;', ' ')
                solutions = get_img(solutions)
                data_dict['solution'] = solutions
                data.append(data_dict)
        elif '不定项选择题' in part_title:
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 输出结果
            solutions = eval(solutions.replace('&nbsp;', ' '))
            for i in range(0, options_num):
                data_dict = {}
                data_dict['题目类型'] = part_title
                title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                option = options[i]['options']
                for k, v in option.items():
                    option = '{}.{}'.format(k, v)
                    data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
                title = get_img(title)
                data_dict['题目'] = title
                answer = json.loads(answers)[i].replace(',', '').replace('&nbsp;', ' ')
                answer = get_img(answer)
                data_dict['answer'] = answer
                solution = get_img(solutions[i])
                data_dict['solution'] = solution
                data.append(data_dict)
        elif any(keyword in part_title for keyword in ['综合分析题', '计算问答题', '问答题']):
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 输出结果
            solutions = solutions.replace('&nbsp;', ' ')
            if '[' in solutions[0] and ']' in solutions[-1]:
                solutions = eval(solutions)
            for i in range(0, options_num):
                data_dict = {}
                data_dict['题目类型'] = part_title
                title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                if answers.replace('[', '').replace(']', '').replace('"', '').replace(',', ''):
                    option = options[i]['options']
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
                    title = get_img(title)
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '').replace('&nbsp;', ' ')
                    answer = get_img(answer)
                    data_dict['answer'] = answer
                    solution = solutions[i]
                    solution = get_img(solution)
                    data_dict['solution'] = solution
                    data.append(data_dict)
                else:
                    title = get_img(title)
                    data_dict['题目'] = title
                    data_dict['answer'] = ''
                    solution = solutions[i]
                    solution = get_img(solution)
                    data_dict['solution'] = solution
                    data.append(data_dict)
                print(data_dict)
        else:
            data_dict['题目类型'] = part_title
            for k, v in options.items():
                option = '{}.{}'.format(k, v)
                data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
            answer = question['answer'].replace(',', '').replace('&nbsp;', ' ')
            answer = get_img(answer)
            data_dict['answer'] = answer
            solution = question['solution']
            solution = get_img(solution.replace('&nbsp;', ' '))
            data_dict['solution'] = solution
            data.append(data_dict)
        print(data_dict)
df = pd.DataFrame(data)
df.rename(columns={'solution': '解析', 'answer': '正确答案'}, inplace=True)
df = df[['题目类型', '题目', '解析', '正确答案'] + [col for col in df.columns if '答案' in col and col != '正确答案']]
df['题目类型'] = df['题目类型'].apply(lambda x: ','.join(x.split('、')[1:]) if '、' in x else x)
df['正确答案'] = df['正确答案'].apply(replace_empty_list)
df.fillna('', inplace=True)
result = df.applymap(remove_span_tags)
result.to_csv(f"{exam_name}.csv", encoding='gbk', errors='ignore', index=False)
