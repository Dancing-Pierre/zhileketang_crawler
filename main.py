# -*- coding: utf-8 -*-
import json
import random
import re
import time

import pandas as pd
import requests


def remove_span_tags(text):
    """
    去除span标签
    :param text:
    :return:
    """
    return re.sub(r'<span[^>]*>(.*?)<\/span>', r'\1', text)


def get_exam_detail(exam_list):
    """
    获取试卷详情
    :param exam_list:
    :return:
    """
    page = 1
    for exam_id in exam_list:
        print(f'开始采集试卷：{exam_id}')
        url = 'https://www.zlketang.com/wxpub/api/exam_question?exam_id={}&devtype=web'.format(exam_id)
        a = requests.get(url, headers=header)
        if a.status_code == 200:
            response = json.loads(a.text)
            if 'data' in str(response):
                exam_name = str(response['data']['exam_name']).replace('\t', '').replace('\n', '').strip()
                try:
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
                                        all_options.append(
                                            data_dict['题目'] + per_trouble['description'].replace('&nbsp;', ' '))
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
                                solutions = get_img(solutions)
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
                            elif any(keyword in part_title for keyword in
                                     ['综合分析题', '计算分析题', '计算问答题', '问答题']):
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
                    df = df[['题目类型', '题目', '解析', '正确答案'] + [col for col in df.columns if
                                                                        '答案' in col and col != '正确答案']]
                    df['题目类型'] = df['题目类型'].apply(lambda x: ','.join(x.split('、')[1:]) if '、' in x else x)
                    df['正确答案'] = df['正确答案'].apply(replace_empty_list)
                    df.fillna('', inplace=True)
                    result = df.applymap(remove_span_tags)
                    result.to_csv(f"{page}.{exam_id}_{exam_name}.csv", encoding='gbk', errors='ignore', index=False)
                    page = page + 1
                    time.sleep(random.randint(2, 4))
                except Exception as e:
                    print('报错如下：{}，可以尝试换cookie重启程序，如不行再联系开发者！'.format(e))
                    pass
        else:
            print('网络问题or反爬，采集失败！')


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


def get_exam_id(subject_id, t, tab_name, is_get):
    """
    获取试卷列表页ID
    :param subject_id: 考卷id
    :param t: 时间戳
    :param tab_name:板块名称
    :param is_get:是否需要中途采集
    :return:
    """
    url = f'https://www.zlketang.com/wxpub/api/simulation_v7?from=web&channel=web&devtype=web&platform_type=web&subject_id={subject_id}&t={t}'
    a = requests.get(url=url, headers=header)
    exam_dict = {}
    if a.status_code == 200:
        response = json.loads(a.text)
        vip_data = response['data']['all_exam_types']
        for i in vip_data:
            type_key = i['name']
            if type_key == tab_name:
                type_data = i['exam_list']
                type_value = []
                if is_get:
                    is_get = is_get.strip().replace(' ', '')
                    arrive = False
                    for per_data in type_data:
                        exam_id = per_data['exam_id']
                        exam_name = per_data['exam_name'].strip().replace(' ', '')
                        if arrive:
                            type_value.append(exam_id)
                        else:
                            if is_get in exam_name:
                                arrive = True
                                type_value.append(exam_id)
                else:
                    for per_data in type_data:
                        exam_id = per_data['exam_id']
                        type_value.append(exam_id)
                exam_dict[type_key] = type_value
    else:
        exam_dict = '网络问题or反爬，采集失败！'
    return exam_dict


def replace_empty_list(option):
    """
    空列表
    :param option:
    :return:
    """
    if '[' in option and ']' in option:
        for i in eval(option):
            if not i:
                return None
            else:
                return option
    else:
        return option


if __name__ == '__main__':
    # # 获取当前日期和时间
    # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # a = datetime.strptime('20240704', "%Y%m%d").strftime("%Y-%m-%d %H:%M:%S")
    # if current_time <= a:
    tab_dict = {1: '章节练习', 2: '模拟试卷', 3: '历年真题', 4: 'VIP押题'}
    print('\033[0;34m======================之了课堂采集程序========================\033[0m')
    while True:
        tab_id = int(
            input('\033[1;36m请输入想采集的板块的ID\n选择列表【1-章节练习|2-模拟试卷|3-历年真题|4-VIP押题】：\033[0m'))
        if tab_id in [1, 2, 3, 4]:
            break
        else:
            print('\033[31m**输入错误，请从中选择ID【1-章节练习|2-模拟试卷|3-历年真题|4-VIP押题】!!\033[0m')
    tab_name = tab_dict[tab_id]
    print(f'\033[31m采集限制- {tab_name} -模块\033[0m')
    try:
        subject_id = input('请输入参数subject_id：')
        t = input('请输入参数t：')
        cookie = input('请输入cookie：')
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
        is_get = input('是否需要从中途采集，如需要输入试卷名，不需要就直接回车！！：')
        exam_list = get_exam_id(subject_id, t, tab_name, is_get)
        print(f'\033[31m采集列表如下：{exam_list}\033[0m')
        get_exam_detail(exam_list[tab_name])
        input('回车退出程序')
    except Exception as e:
        print('报错如下：{}，请联系开发者！'.format(e))
        input('回车退出程序')
    # else:
    #     print('试用到期！！')
    #     input('回车退出程序')
