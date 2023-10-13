# -*- coding: utf-8 -*-
import csv
import json
import random
import re
import time

import requests


def get_exam_id(subject_id, t, exam_chinese_name):
    url = 'https://www.zlketang.com/wxpub/api/simulationv4?from=web&channel=web&devtype=web&platform_type=web&subject_id={}&t={}'.format(
        subject_id, t)
    a = requests.get(url=url, headers=header)
    exam_dict = {}
    get_name = False
    if a.status_code == 200:
        response = json.loads(a.text)
        vip_data = response['data']['VIP保过题库']
        for per_data in vip_data:
            exam_id = per_data['exam_id']
            exam_name = per_data['exam_name']
            upgrade_info_str = per_data["upgrade_info"]
            upgrade_info_json = json.loads(upgrade_info_str)
            if upgrade_info_json['year'] == '2023' or '押题' in exam_name or upgrade_info_json['year'] == 2023:
                exam_name_replace = exam_name.replace(' ', '')
                exam_chinese_name_replace = exam_chinese_name.replace(' ', '')
                if exam_name_replace == exam_chinese_name_replace or get_name:
                    get_name = True
                    exam_dict[f'{exam_name}'] = exam_id
    else:
        exam_dict = '网络问题or反爬，采集失败！'
    return exam_dict


def get_exam_detail(exam_dict):
    page = 1
    for exam_name in exam_dict:
        exam_id = exam_dict[exam_name]
        print(f'开始采集试卷：{exam_id}')
        url = 'https://www.zlketang.com/wxpub/api/exam_question?exam_id={}&devtype=web'.format(exam_id)
        a = requests.get(url, headers=header)
        if a.status_code == 200:
            response = json.loads(a.text)
            exam_name = str(response['data']['exam_name']).strip()
            try:
                data = []
                print(exam_name)
                detail = response['data']['parts']
                # 类型：选择、填空、判断
                for per_part in detail:
                    part_title = per_part['title']
                    if exam_id == 5646 or exam_id == '5646':
                        part_title = '不定项选择题'
                    elif exam_id == 15114 or exam_id == '15114':
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
                        if '计算' in part_title or '综合题' in part_title or '简答题' in part_title or '案例分析' in part_title:
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
                        elif '不定项选择题' in part_title:
                            answers = question['answer']
                            # 题干
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
                                data_dict['number'] = 7
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
                with open(f"{page}.{exam_name}.csv", mode="w", newline="", encoding='gbk', errors='ignore') as csvfile:
                    fieldnames = ["number", "title", "option", "option_num", "answer", "solution"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    for row in data:
                        writer.writerow(row)
                page = page + 1
                time.sleep(random.randint(2, 4))
            except Exception as e:
                print('报错如下：{}，可以尝试换cookie重启程序，如不行再联系开发者！'.format(e))
                break
        else:
            print('网络问题or反爬，采集失败！')


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
    try:
        subject_id = input('请输入参数subject_id：')
        t = input('请输入参数t：')
        cookie = input('请输入cookie：')
        exam_chinese_name = input('请输入想要开始采集的试卷名：')
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8",
            "Cookie": cookie,
            "Referer": 'https://www.zlketang.com/personal/index.html?name=1',
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        a = get_exam_id(subject_id, t, exam_chinese_name)
        print(f'本次采集的试卷列表：{a}')
        if a == '网络问题or反爬，采集失败！':
            print('采集失败，已结束程序！！！')
            input('回车退出程序')
        else:
            get_exam_detail(a)
            print('===========程序结束！！==========')
            input('回车退出程序')
    except Exception as e:
        print('报错如下：{}，请联系开发者！'.format(e))
        input('回车退出程序')
