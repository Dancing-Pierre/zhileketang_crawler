# -*- coding: utf-8 -*-
import csv
import json
import random
import re
import time

import requests


def get_exam_detail():
    with open('1111.json', 'r', encoding='utf8') as f:
        # 读取json文件
        response = json.load(f)
    exam_name = str(response['data']['exam_name']).strip()
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
            question_title = clean.sub('', question_title)
            data_dict['title'] = question_title.replace('&nbsp;', ' ')
            options = question['options']
            options = json.loads(re.sub(clean, '', options))
            if '综合题' in part_title or '简答题' in part_title or '案例分析' in part_title:
                data_dict['number'] = 6
                all_option = ''
                if type(options) == list:
                    option_num = len(options)
                    for per_trouble in options:
                        all_option = all_option + '<p>{}</p>'.format(
                            per_trouble['description'].replace('&nbsp;', ' '))
                    data_dict['option'] = all_option
                    data_dict['option_num'] = option_num
                else:
                    data_dict['option'] = ''
                    data_dict['option_num'] = 0
                answer = question['answer']
                if type(answer) == list:
                    all_answers = ''
                    answers = json.loads(answer)
                    for answer in answers:
                        all_answers = all_answers + answer.replace('&nbsp;', ' ')
                    data_dict['answer'] = all_answers
                else:
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                solution = question['solution']
                get_img(solution, exam_name, part_title)
                solution = re.sub(clean, '', solution)
                if type(solution) == list:
                    all_solutions = ''
                    solutions = json.loads(solution)
                    for solution in solutions:
                        all_solutions = all_solutions + solution.replace('&nbsp;', ' ')
                    data_dict['solution'] = all_solutions
                else:
                    data_dict['solution'] = solution.replace('&nbsp;', ' ')
                data.append(data_dict)
            elif '计算题' in part_title:
                answers = question['answer']
                # 题干
                question_title = clean.sub('', question_title)
                question_title = question_title.replace('&nbsp;', ' ')
                options_num = len(options)
                solutions = question['solution']
                cleaned_text = clean_html_css(solutions)
                # 提取图片
                get_img(solutions, exam_name, '计算题')
                # 输出结果
                solutions = eval(cleaned_text.replace('&nbsp;', ' '))
                for i in range(0, options_num):
                    data_dict = {}
                    data_dict['number'] = 9
                    title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                    option = options[i]['options']
                    all_option = ''
                    option_num = len(option.items())
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        all_option = all_option + '<p>{}</p>'.format(option.replace('&nbsp;', ' '))
                    data_dict['title'] = title
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data_dict['option'] = all_option
                    data_dict['option_num'] = option_num
                    data.append(data_dict)
            elif '不定项选择题' in part_title:
                answers = question['answer']
                # 题干
                question_title = clean.sub('', question_title)
                question_title = question_title.replace('&nbsp;', ' ')
                options_num = len(options)
                solutions = question['solution']
                cleaned_text = clean_html_css(solutions)
                # 提取图片
                get_img(solutions, exam_name, '不定项选择题')
                # 输出结果
                solutions = eval(cleaned_text.replace('&nbsp;', ' '))
                for i in range(0, options_num):
                    data_dict = {}
                    data_dict['number'] = 7
                    title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                    option = options[i]['options']
                    all_option = ''
                    option_num = len(option.items())
                    for k, v in option.items():
                        option = '{}.{}'.format(k, v)
                        all_option = all_option + '<p>{}</p>'.format(option.replace('&nbsp;', ' '))
                    data_dict['title'] = title
                    data_dict['option'] = all_option
                    data_dict['option_num'] = option_num
                    answer = json.loads(answers)[i].replace(',', '')
                    data_dict['answer'] = answer.replace('&nbsp;', ' ')
                    data_dict['solution'] = solutions[i]
                    data.append(data_dict)
            elif '综合分析题' in part_title:
                answers = question['answer']
                # 题干
                question_title = clean.sub('', question_title)
                question_title = question_title.replace('&nbsp;', ' ')
                options_num = len(options)
                solutions = question['solution']
                cleaned_text = clean_html_css(solutions)
                # 提取图片
                get_img(solutions, exam_name, '综合分析题')
                # 输出结果
                solutions = eval(cleaned_text.replace('&nbsp;', ' '))
                for i in range(0, options_num):
                    data_dict = {}
                    data_dict['number'] = 10
                    title = question_title + options[i]['description'].replace('&nbsp;', ' ')
                    if answers.replace('[', '').replace(']', '').replace('"', '').replace(',', ''):
                        option = options[i]['options']
                        all_option = ''
                        option_num = len(option.items())
                        for k, v in option.items():
                            option = '{}.{}'.format(k, v)
                            all_option = all_option + '<p>{}</p>'.format(option.replace('&nbsp;', ' '))
                        data_dict['title'] = title
                        answer = json.loads(answers)[i].replace(',', '')
                        data_dict['answer'] = answer.replace('&nbsp;', ' ')
                        data_dict['solution'] = solutions[i]
                        data_dict['option'] = all_option
                        data_dict['option_num'] = option_num
                        data.append(data_dict)
                    else:
                        data_dict['title'] = title
                        data_dict['answer'] = ''
                        data_dict['solution'] = solutions[i]
                        data_dict['option'] = ''
                        data_dict['option_num'] = 0
                        data.append(data_dict)
            else:
                if '单选题' in part_title or '单项选择题' in part_title:
                    data_dict['number'] = 1
                elif '多选题' in part_title or '多项选择题' in part_title:
                    data_dict['number'] = 2
                elif '判断题' in part_title:
                    data_dict['number'] = 3
                else:
                    data_dict['number'] = 0
                all_option = ''
                option_num = len(options.items())
                for k, v in options.items():
                    option = '{}.{}'.format(k, v)
                    all_option = all_option + '<p>{}</p>'.format(option.replace('&nbsp;', ' '))
                data_dict['option'] = all_option
                data_dict['option_num'] = option_num
                answer = question['answer'].replace(',', '')
                data_dict['answer'] = answer.replace('&nbsp;', ' ')
                solution = question['solution']
                get_img(solution, exam_name, part_title)
                solution = re.sub(clean, '', solution)
                data_dict['solution'] = solution.replace('&nbsp;', ' ')
                data.append(data_dict)
            print(data_dict)
    with open(f"{exam_name}.csv", mode="w", newline="", encoding='gbk', errors='ignore') as csvfile:
        fieldnames = ["number", "title", "option", "option_num", "answer", "solution"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for row in data:
            writer.writerow(row)


def clean_html_css(text):
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除CSS样式
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text)
    return text


def get_img(text, exam_name, part_name):
    # 提取img标签中的src属性值
    img_src_list = []
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
            img_url = 'https://image.zlketang.com' + url
            r = requests.get(img_url)
            with open(f"{exam_name}_{part_name}_{i}.png", "wb") as f:  # wb是写二进制
                f.write(r.content)
            time.sleep(1)


if __name__ == '__main__':
    get_exam_detail()
