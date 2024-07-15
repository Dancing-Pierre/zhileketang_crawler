# -*- coding: utf-8 -*-
import json
import re
import time

import numpy as np
import pandas as pd
import requests


def get_img(text):
    """
    下载图片
    :param text:
    :return:
    """
    img_src_list = []
    if text:
        if text[0] == '[' and text[-1] == ']':
            html_text = json.loads(text)
            for text in html_text:
                img_src_list.extend(re.findall(r'<img\s+src="([^"]+)"', text))
        else:
            html_text = text
            img_src_list.extend(re.findall(r'<img\s+src="([^"]+)"', html_text))
        if img_src_list:
            for i in range(0, len(img_src_list)):
                url = img_src_list[i]
                file_name = url.split('/')[-1]
                if 'https://' in url:
                    img_url = url
                else:
                    img_url = 'https://image.zlketang.com' + url
                r = requests.get(img_url)
                with open(file_name, "wb") as f:  # wb是写二进制
                    f.write(r.content)
                time.sleep(1)


def split_options(option_str):
    # 使用正则表达式匹配选项
    pattern = re.compile(r'([A-Z]\.[^A-Z]*)')
    matches = pattern.findall(option_str)
    option_dict = {}
    for match in matches:
        key = match[0]  # 获取选项的字母
        option_dict[f'答案{key}'] = '<p>' + match.strip() + '</p>'  # 去掉两端的空格
    return option_dict


def replace_empty_list(option):
    if '[' in option and ']' in option:
        for i in eval(option):
            if not i:
                return None
            else:
                return option
    else:
        return option


with open('2024年注会《经济法》第一次万人模考卷.json', 'r', encoding='utf-8') as file:
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
        clean = re.compile(r'<(?!\/?(p|br)\b)[^>]+>')
        question_title = question['description']
        # 提取图片
        get_img(question_title)
        question_title = clean.sub('', question_title)
        data_dict['题目'] = question_title.replace('&nbsp;', ' ')
        options = question['options']
        options = json.loads(re.sub(clean, '', options))
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
            get_img(solution)
            solution = re.sub(clean, '', solution)
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
            question_title = clean.sub('', question_title)
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            get_img(solutions)
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
                        all_option = all_option + option.replace('&nbsp;', ' ')
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data_dict['option'] = all_option
                    data.append(data_dict)
            else:
                data_dict['题目类型'] = part_title
                data_dict['题目'] = question_title
                data_dict['answer'] = answers
                data_dict['solution'] = solutions.replace('&nbsp;', ' ')
                data_dict['option'] = ''
                data.append(data_dict)
        elif '不定项选择题' in part_title:
            answers = question['answer']
            # 题干
            question_title = clean.sub('', question_title)
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            # 提取图片
            get_img(solutions)
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
                    all_option = all_option + option.replace('&nbsp;', ' ')
                data_dict['题目'] = title
                data_dict['option'] = all_option
                answer = json.loads(answers)[i].replace(',', '')
                data_dict['answer'] = answer.replace('&nbsp;', ' ')
                data_dict['solution'] = solutions[i]
                data.append(data_dict)
        elif any(keyword in part_title for keyword in ['综合分析题', '计算分析题', '计算问答题', '问答题']):
            answers = question['answer']
            # 题干
            question_title = clean.sub('', question_title)
            question_title = question_title.replace('&nbsp;', ' ')
            options_num = len(options)
            solutions = question['solution']
            cleaned_text = solutions
            # 提取图片
            get_img(solutions)
            # 输出结果
            cleaned_text = cleaned_text.replace('&nbsp;', ' ')
            if '[' in cleaned_text[0] and ']' in cleaned_text[-1]:
                solutions = eval(cleaned_text)
            for i in range(0, options_num):
                data_dict = {}
                data_dict['题目类型'] = part_title
                title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                if answers.replace('[', '').replace(']', '').replace('"', '').replace(',', ''):
                    option = options[i]['options']
                    all_option = ''
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        all_option = all_option + option.replace('&nbsp;', ' ')
                    data_dict['题目'] = title
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data_dict['option'] = all_option
                    data.append(data_dict)
                else:
                    data_dict['题目'] = title
                    data_dict['answer'] = ''
                    data_dict['solution'] = solutions[i]
                    data_dict['option'] = ''
                    data.append(data_dict)
                print(data_dict)
        else:
            data_dict['题目类型'] = part_title
            all_option = ''
            for k, v in options.items():
                option = '{}.{}'.format(k, v)
                all_option = all_option + option.replace('&nbsp;', ' ')
            data_dict['option'] = all_option
            answer = question['answer'].replace(',', '')
            data_dict['answer'] = answer.replace('&nbsp;', ' ')
            solution = question['solution']
            get_img(solution)
            solution = re.sub(clean, '', solution)
            data_dict['solution'] = solution.replace('&nbsp;', ' ')
            data.append(data_dict)
        print(data_dict)
df = pd.DataFrame(data)
df.rename(columns={'solution': '解析', 'answer': '正确答案'}, inplace=True)
df = df[['题目类型', '题目', '解析', '正确答案', 'option']]
df['题目类型'] = df['题目类型'].apply(lambda x: ','.join(x.split('、')[1:]) if '、' in x else x)
df['option'].fillna('', inplace=True)
options_split = df['option'].apply(split_options)
options_df = pd.DataFrame(options_split.tolist())
result_df = pd.concat([df, options_df], axis=1).drop(columns=['option'])
result_df['正确答案'] = result_df['正确答案'].apply(replace_empty_list)
result_df.to_csv(f"{exam_name}.csv", encoding='gbk', errors='ignore', index=False)
