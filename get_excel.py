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
                if exam_name == exam_chinese_name or get_name:
                    get_name = True
                    exam_dict[f'{exam_name}'] = exam_id
    else:
        exam_dict = '网络问题or反爬，采集失败！'
    return exam_dict


def get_exam_detail(exam_dict):
    for exam_name in exam_dict:
        exam_id = exam_dict[exam_name]
        print(f'开始采集试卷：{exam_id}')
        url = 'https://www.zlketang.com/wxpub/api/exam_question?exam_id={}&devtype=web'.format(exam_id)
        a = requests.get(url, headers=header)
        if a.status_code == 200:
            response = json.loads(a.text)
            exam_name = response['data']['exam_name']
            try:
                data = []
                print(exam_name)
                detail = response['data']['parts']
                i = 1
                # 类型：选择、填空、判断
                for per_part in detail:
                    part_title = per_part['title']
                    questions = per_part['questions']
                    # 每个问题
                    for question in questions:
                        data_dict = {}
                        clean = re.compile('<.*?>')
                        question_title = question['description']
                        question_title = re.sub(clean, '', question_title)
                        data_dict['number'] = i
                        data_dict['title'] = question_title.replace('&nbsp;', ' ')
                        options = question['options']
                        options = json.loads(re.sub(clean, '', options))
                        if '计算' in part_title or '综合题' in part_title or '简答题' in part_title or '案例分析' in part_title:
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
                            if '[' in answer:
                                all_answers = ''
                                answers = json.loads(answer)
                                for answer in answers:
                                    all_answers = all_answers + answer.replace('&nbsp;', ' ')
                                data_dict['answer'] = all_answers
                            else:
                                data_dict['answer'] = answer.replace('&nbsp;', ' ')
                            solution = question['solution']
                            solution = re.sub(clean, '', solution)
                            if '[' in solution:
                                all_solutions = ''
                                solutions = json.loads(solution)
                                for solution in solutions:
                                    all_solutions = all_solutions + solution.replace('&nbsp;', ' ')
                                data_dict['solution'] = all_solutions
                            else:
                                data_dict['solution'] = solution.replace('&nbsp;', ' ')
                        else:
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
                            solution = re.sub(clean, '', solution)
                            data_dict['solution'] = solution.replace('&nbsp;', ' ')
                        i = 1 + i
                        data.append(data_dict)
                        print(data_dict)
                with open(f"{exam_name}.csv", mode="w", newline="", encoding="utf-8") as csvfile:
                    fieldnames = ["number", "title", "option", "option_num", "answer", "solution"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    for row in data:
                        writer.writerow(row)
                time.sleep(random.randint(2, 4))
            except Exception as e:
                print('报错如下：{}，可以尝试换cookie重启程序，如不行再联系开发者！'.format(e))
                break
        else:
            print('网络问题or反爬，采集失败！')


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
            pass
        else:
            get_exam_detail(a)
            print('===========程序结束！！==========')
    except Exception as e:
        print('报错如下：{}，请联系开发者！'.format(e))
        time.sleep(30)
