import re
import urllib2
import bs4
import json
import requests
import sys
import traceback
import progressbar
from data_center.models import *

url = 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/6/6.2/6.2.9/JH629002.php'
YS = '103|20'
cond = 'a'

cou_codes = ['ANTH', 'ANTU', 'ASTR', 'BME ', 'BMES', 'CF ', 'CFGE', 'CHE ', 'CHEM', 'CL ', 'CLC ', 'CLU ', 'COM ', 'CS ', 'DL ', 'DMS ', 'E ', 'ECON', 'EE ', 'EECS', 'EMBA', 'ENE ', 'ESS ', 'FL ', 'FLU ', 'GE ', 'GEC ', 'GEU ', 'GPTS', 'HIS ', 'HSS ', 'HSSU', 'IACS', 'IACU', 'IEEM', 'IEM ', 'ILS ', 'IMBA', 'IPE ', 'IPNS', 'IPT ', 'ISA ', 'ISS ', 'LANG', 'LING', 'LS ', 'LSBS', 'LSBT', 'LSIP', 'LSMC', 'LSMM', 'LSSN', 'LST ', 'MATH', 'MATU', 'MBA ', 'MI ', 'MS ', 'NEMS', 'NES ', 'NS ', 'NUCL', 'PE ', 'PE1 ', 'PE3 ', 'PHIL', 'PHYS', 'PHYU', 'PME ', 'QF ', 'RB ', 'RDDM', 'RDIC', 'RDPE', 'SCI ', 'SLS ', 'SNHC', 'SOC ', 'STAT', 'STAU', 'TE ', 'TEG ', 'TEX ', 'TIGP', 'TL ', 'TM ', 'UPMT', 'W ', 'WH ', 'WW ', 'WZ ', 'X ', 'XA ', 'XZ ', 'YZ ', 'ZY ', 'ZZ ']


def cou_code_2_html(cou_code, ACIXSTORE, auth_num):
    try:
        r = requests.post(url,
            data={
                'ACIXSTORE': ACIXSTORE,
                'YS': YS,
                'cond': cond,
                'cou_code': cou_code,
                'auth_num': auth_num})
        return r.text.encode('latin1', 'ignore').decode('big5', 'ignore')
    except:
        print traceback.format_exc()
        print cou_code
        return 'QAQ, what can I do?'


def trim_td(td):
    return td.get_text().rstrip().lstrip().encode('utf8', 'ignore')


def tr_2_class_info(tr):
    tds = tr.find_all('td')
    class_info = {
        'no': trim_td(tds[0]),
        'title': trim_td(tds[1]),
        'credit': trim_td(tds[2]),
        'time': trim_td(tds[3]),
        'room': trim_td(tds[4]),
        'teacher': trim_td(tds[5]),
        'limit': trim_td(tds[6]),
        'note': trim_td(tds[7]),
        'object': trim_td(tds[9]),
        'prerequisite': trim_td(tds[10])
    }
    return class_info


def initial_db(ACIXSTORE, auth_num):
    progress = progressbar.ProgressBar()
    class_infos = []
    total_collected = 0
    for cou_code in progress(cou_codes):
        html = cou_code_2_html(cou_code, ACIXSTORE, auth_num)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        trs = soup.find_all('tr')
        trs = [tr for tr in trs if 'class3' in tr['class'] and len(tr.find_all('td')) > 1]
        for tr in trs:
            try:
                class_info = tr_2_class_info(tr)
                class_infos.append(class_info)
                if not class_info['credit']:
                    class_info['credit'] = '0'
                if not class_info['limit']:
                    class_info['limit'] = '0'
                Course.objects.filter(title=class_info['title']).delete()
                Course.objects.create(
                    no=class_info['no'],
                    title=class_info['title'],
                    credit=int(class_info['credit']),
                    time=class_info['time'],
                    room=class_info['room'],
                    teacher=class_info['teacher'],
                    limit=int(class_info['limit']),
                    note=class_info['note'],
                    object=class_info['object'],
                    prerequisite=class_info['prerequisite'] != ''
                )
                total_collected += 1
            except :
                print 'QAQ, what can I do?'
                print traceback.format_exc()

    print 'Crawling process is done. %d course information collected.' % total_collected

