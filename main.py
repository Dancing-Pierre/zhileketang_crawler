# -*- coding: utf-8 -*-
import binascii
import json
import random
import re
import time

import pandas as pd
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from fake_useragent import UserAgent


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
        url = 'https://www.zlketang.com/wxpub/api/exam_detail?from=web&channel=web&devtype=web&platform_type=web&exam_id={}'.format(
            exam_id)
        a = requests.get(url, headers=header)
        if a.status_code == 200:
            response = json.loads(a.text)
            try:
                EXAM_AES_KEY = "nm5387945d5d4c91047b3b50234ca7ak"
                # 解析UTF-8格式的AES密钥
                aes_key = EXAM_AES_KEY.encode('utf-8')
                # 将加密的数据从16进制格式解析为字节
                encrypted_bytes = binascii.unhexlify(response['data']['parts'])
                # 创建一个AES密码对象，使用ECB模式和PKCS7填充
                cipher = AES.new(aes_key, AES.MODE_ECB)
                # 解密数据
                decrypted_bytes = cipher.decrypt(encrypted_bytes)
                # 去掉PKCS7填充的内容
                decrypted_data = unpad(decrypted_bytes, AES.block_size)
                # 将解密后的数据转换为UTF-8字符串
                decrypted_string = decrypted_data.decode('utf-8')
                data = json.loads(decrypted_string)
                response['data']['parts'] = data
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
                            if type(eval(answer)) == list:
                                answers = json.loads(answer)
                                for answer in answers:
                                    answer = answer.replace('&nbsp;', ' ')
                                    answer = get_img(answer)
                                    all_answers.append(answer)
                            solution = question['solution']
                            all_solutions = []
                            if type(eval(solution)) == list:
                                solutions = json.loads(solution)
                                for solution in solutions:
                                    solution = solution.replace('&nbsp;', ' ')
                                    solution = get_img(solution)
                                    all_solutions.append(solution)
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
                df = df[['题目类型', '题目', '解析', '正确答案'] + [col for col in df.columns if
                                                                    '答案' in col and col != '正确答案']]
                df['题目类型'] = df['题目类型'].apply(lambda x: ','.join(x.split('、')[1:]) if '、' in x else x)
                df['正确答案'] = df['正确答案'].apply(replace_empty_list)
                df.fillna('', inplace=True)
                result = df.applymap(remove_span_tags)
                result.to_csv(f"{page}.{exam_id}_{exam_name}.csv", encoding='gbk', errors='ignore', index=False)
                page = page + 1
                time.sleep(random.randint(3, 8))
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
    global img_list
    img_src_list = []
    if text:
        img_src_list.extend(re.findall(r'<img\s+src="([^"]+)"', text))
        if img_src_list:
            for i in range(0, len(img_src_list)):
                url = img_src_list[i]
                file_name = url.split('/')[-1]
                if file_name not in img_list:
                    img_list.append(file_name)
                    new_file_name = '/public/images/' + file_name
                    if 'https://' in url:
                        img_url = url
                    else:
                        img_url = 'https://image.zlketang.com' + url
                    print(f'** 采集图片 {img_url}')
                    r = requests.get(url=img_url, headers=header)
                    with open(file_name, "wb") as f:  # wb是写二进制
                        f.write(r.content)
                    text = text.replace(url, new_file_name)
                    time.sleep(random.randint(1, 5))
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
    img_list = []
    tab_dict = {1: '章节练习', 2: '模拟试卷', 3: '历年真题', 4: 'VIP押题'}
    print('======================之了课堂采集程序========================')
    while True:
        tab_id = int(
            input('请输入想采集的板块的ID\n选择列表【1-章节练习|2-模拟试卷|3-历年真题|4-VIP押题】：'))
        if tab_id in [1, 2, 3, 4]:
            break
        else:
            print('**输入错误，请从中选择ID【1-章节练习|2-模拟试卷|3-历年真题|4-VIP押题】!!')
    tab_name = tab_dict[tab_id]
    print(f'采集限制- {tab_name} -模块')
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
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }
        is_get = input('是否需要从中途采集，如需要输入试卷名，不需要就直接回车！！：')
        exam_list = get_exam_id(subject_id, t, tab_name, is_get)
        print(f'采集列表如下：{exam_list}')
        get_exam_detail(exam_list[tab_name])
        input('回车退出程序')
    except Exception as e:
        print('报错如下：{}，请联系开发者！'.format(e))
        input('回车退出程序')
