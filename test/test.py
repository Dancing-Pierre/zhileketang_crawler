# -*- coding: utf-8 -*-
import json
import re
import time

import numpy as np
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


with open('2.2终值和现值★★★.json', 'r', encoding='utf-8') as file:
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
    # 每个问题
    for question in questions:
        data_dict = {}
        question_title = question['description']
        # 提取图片
        question_title = get_img(question_title)
        data_dict['题目'] = question_title.replace('&nbsp;', ' ')
        options = question['options']
        options = json.loads(options)
        if '综合题' in part_title or '简答题' in part_title or '案例分析' in part_title:
            all_options = []
            if type(options) == list:
                for per_trouble in options:
                    all_options.append(data_dict['题目'] + per_trouble['description'].replace('&nbsp;', ' '))
            answer = question['answer']
            all_answers = []
            if type(eval(answer)) == list:
                answers = json.loads(answer)
                for answer in answers:
                    all_answers.append(answer.replace('&nbsp;', ' '))
            solution = question['solution']
            solution = get_img(solution)
            all_solutions = []
            if type(eval(solution)) == list:
                solutions = json.loads(solution)
                for solution in solutions:
                    all_solutions.append(solution.replace('&nbsp;', ' '))
            zipped = zip(all_options, all_answers, all_solutions)
            for per_zip in list(zipped):
                data_dict = {'题目类型': part_title, '题目': per_zip[0], 'answer': per_zip[1], 'solution': per_zip[2]}
                data.append(data_dict)
        elif '计算题' in part_title:
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            solutions = get_img(solutions)
            if options:
                # 输出结果
                solutions = eval(solutions.replace('&nbsp;', ' '))
                for i in range(0, options_num):
                    data_dict = {}
                    data_dict['题目类型'] = part_title
                    title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                    option = options[i]['options']
                    all_option = ''
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data.append(data_dict)
            else:
                data_dict['题目类型'] = part_title
                data_dict['题目'] = question_title
                data_dict['answer'] = answers
                data_dict['solution'] = solutions.replace('&nbsp;', ' ')
                data.append(data_dict)
        elif '不定项选择题' in part_title:
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            solutions = get_img(solutions)
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
                data_dict['题目'] = title
                answer = json.loads(answers)[i].replace(',', '')
                data_dict['answer'] = answer.replace('&nbsp;', ' ')
                data_dict['solution'] = solutions[i]
                data.append(data_dict)
        elif any(keyword in part_title for keyword in ['综合分析题', '计算分析题', '计算问答题', '问答题']):
            answers = question['answer']
            # 题干
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            solutions = get_img(solutions)
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
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data.append(data_dict)
                else:
                    data_dict['题目'] = title
                    data_dict['answer'] = ''
                    data_dict['solution'] = solutions[i]
                    data.append(data_dict)
                print(data_dict)
        else:
            data_dict['题目类型'] = part_title
            all_option = ''
            for k, v in options.items():
                option = '{}.{}'.format(k, v)
                data_dict[f'答案{k}'] = '<p>' + option.replace('&nbsp;', ' ') + '</p>'
            answer = question['answer'].replace(',', '')
            data_dict['answer'] = answer.replace('&nbsp;', ' ')
            solution = question['solution']
            solution = get_img(solution)
            data_dict['solution'] = solution.replace('&nbsp;', ' ')
            data.append(data_dict)
        print(data_dict)
df = pd.DataFrame(data)
df.rename(columns={'solution': '解析', 'answer': '正确答案'}, inplace=True)
df = df[['题目类型', '题目', '解析'] + [col for col in df.columns if '答案' in col]]
df['题目类型'] = df['题目类型'].apply(lambda x: ','.join(x.split('、')[1:]) if '、' in x else x)
df['正确答案'] = df['正确答案'].apply(replace_empty_list)
df.fillna('', inplace=True)
result = df.applymap(remove_span_tags)
result.to_csv(f"{exam_name}.csv", encoding='gbk', errors='ignore', index=False)
