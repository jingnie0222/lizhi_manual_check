#!/usr/bin/python3
# -*-codig=utf8-*-

import sys
import requests
from urllib.parse import quote
import math
import pysnooper
import DataFile
import Template
import Mail
import random


top_word_loc = "http://$ip/vr_query_period/vr_query_pv.txt"
random_word_loc = "http://$ip/vr_query_period/vr_query_random.txt"

top_word_file = "./word_top"
random_word_file = "./word_random"

url_file = "./url_lizhi"
url_prefix = "https://wap.sogou.com/web/searchList.jsp?keyword="

#mail_lst = ['yinjingjing@sogou-inc.com']
mail_lst = DataFile.read_file_into_list("./mail_list")
report_tmp_path = "mail_detail.html"

def get_word(url, word_file):

    try:
        res = requests.get(url)
        res.encoding = "utf-8"
        with open(word_file, 'w', encoding='utf8') as f:
            f.write(res.text)
    except Exception as err:
        print('[get_word]: %s' % err)


def gen_url(f_in, f_out):
    try:
        for line in f_in.readlines():
            query = line.strip().split('\t')[0]
            url = url_prefix + quote(query)
            f_out.write(query + 2*"\t" + url + "\n")
    except Exception as err:
        print('[gen_url]: %s' % err)


def dispatch_url(urllist, n, i):
    # 将列表切分为n份,返回第i份
    total_len = len(urllist)
    try:
        step = math.ceil(total_len/n)
        if i < n-1 :
            return urllist[i*step:(i+1)*step]
        if i == n-1 :
            return urllist[i*step:]

    except Exception as err:
        print("[dispatch_url]:%s" % err)


if __name__ == "__main__":

    get_word(top_word_loc, top_word_file)
    get_word(random_word_loc, random_word_file)

    with open(url_file, 'w', encoding='utf8') as f_out:
        with open(top_word_file, 'r', encoding='utf8') as f_top:
            gen_url(f_top, f_out)
        with open(random_word_file, 'r', encoding='utf8') as f_ran:
            gen_url(f_ran, f_out)

    mail_count = len(mail_lst)
    url_list = DataFile.read_file_into_list(url_file)
    random.shuffle(url_list)

    if url_list:
        for i in range(mail_count):
            report_content = ""
            mail_url = ""

            mail_title = Template.html_h3_title("请检查如下url的首条立知结果，展示是否正确合理，点出跳转逻辑是否正确合理，如有问题请反馈至xxx")
            mail_to = mail_lst[i]

            temp_url = dispatch_url(url_list, mail_count, i)

            for url in temp_url:
                mail_url += "<p>" + url + "</p>\n"

            report_content = mail_title + mail_url
            DataFile.write_full_file(report_tmp_path, report_content)
            Mail.sendMail("立知TOP词线上走查", report_tmp_path, mail_to)
            print(mail_to)
    else:
        print("url列表为空，请检查是否正确获取到词源")

