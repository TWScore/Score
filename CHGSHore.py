import requests
from pyquery import PyQuery as pq
import pandas as pd
import re
from bs4 import BeautifulSoup as BS

isnan = lambda x:x!=x
is_valid = lambda x:x!='0/0' and not isnan(x)
valid = lambda x:x if is_valid(x) else ''

def get(account=None, password=None, mode='i'):
    if not(account and password):
        raise ValueError('Account or password Error!')
    s = requests.Session()
    login = s.get("http://campus2.chgsh.chc.edu.tw/SCORESTD/Login.aspx")

    soup = BS(login.text, 'html.parser')

    login = s.post("http://campus2.chgsh.chc.edu.tw/SCORESTD/Login.aspx", data={
        '__VIEWSTATE': soup.find('input', id='__VIEWSTATE')['value'],
        '__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
        "__EVENTVALIDATION": soup.find('input', id="__EVENTVALIDATION")['value'],
        'Login_UserId': account,
        'Login_Passwd': password,
        'Login_Submit.x': '0',
        'Login_Submit.y': '0'}) # Login
    # login.encoding = 'big5'
    if "帳號或密碼錯誤!!" in login.text:
        raise ValueError('Account or password Error!')
    login = s.get("http://campus2.chgsh.chc.edu.tw/SCORESTD/Index.aspx")

    def get_score(): # 學期成績
        score = {}
        get_score_data = s.get("http://campus2.chgsh.chc.edu.tw/SCORESTD/BSB03.aspx")
        
        menugroup = BS(get_score_data.text, 'html.parser').find('table', 'MenuGroup')
        links = list(zip(['http://campus2.chgsh.chc.edu.tw/SCORESTD/'+i['href'] for i in menugroup.find_all('a')],
                         [i.text for i in menugroup.find_all('font', 'MenuItem')]))
        for i in links:
            exam = i[1]
            if exam == '學期成績':
                continue
            score_data = pd.read_html(s.get(i[0]).text)[5]
            subjects = [i for i in score_data[0]][1:]
            for j in range(0,len(subjects)):
                try:
                    score[exam].update({subjects[j]:[
                        valid(score_data[2][j+1]),
                        '', 
                        valid(score_data[3][j+1]),
                        valid(score_data[4][j+1]),
                        '']
                    })
                except KeyError:
                    score[exam] = {subjects[j]:[
                        valid(score_data[2][j+1]),
                        '', 
                        valid(score_data[3][j+1]),
                        valid(score_data[4][j+1]),
                        '']
                    }
        score_data = pd.read_html(get_score_data.text)[5]
        rank_data = pd.read_html(get_score_data.text)[8]
        semester_grade = score_data[8][0]
        for i in range(0,len(subjects)):
            try:
                score[semester_grade].update({subjects[i]:[
                    valid(score_data[8][i+1]),
                    '',
                    valid(score_data[12][i+1]),
                    valid(score_data[13][i+1]),
                    '']})
            except KeyError:
                score[semester_grade] = {subjects[i]:[
                    valid(score_data[8][i+1]),
                    '',
                    valid(score_data[12][i+1]),
                    valid(score_data[13][i+1]),
                    '']}
        
        for i in range(9,12):
            exam = score_data[i][0]
            for j in range(0,len(subjects)):
                try:
                    score[exam].update({subjects[j]: [valid(score_data[i][j+1]),'','','','']})
                except KeyError:
                    score[exam] = {subjects[j]: [valid(score_data[i][j+1]),'','','','']}

        rank_titles = [i for i in rank_data[0]][1:]
        for i in range(1,rank_data.shape[1]):
            if rank_data[i][0] in score:
                for j in range(0,len(rank_titles)):
                    score[rank_data[i][0]].update({rank_titles[j]: valid(rank_data[i][j+1])})
            elif rank_data[i][0] + '成績' in score:
                for j in range(0,len(rank_titles)):
                    score[rank_data[i][0] + '成績'].update({rank_titles[j]: valid(rank_data[i][j+1])})
        """
        資料格式: {'第1次平時成績':
                    {'◎ 國文Ⅴ':[ 成績 , 平均 , 排名 , 類組排, 校排],
                    '◎ 英文Ⅴ': ['78', nan, nan, nan],
                    ....,
                    '總分': nan....},
                ....}
        }}
        """
        return score

    def get_info():
        infos = pd.read_html(s.get('http://campus2.chgsh.chc.edu.tw/SCORESTD/BSA01.aspx').text)[1]
        infos = {
            'studentId': valid(infos[1][2]),
            'name': valid(infos[1][3]),
        }
        return infos

    mode_selector = {
        's': get_score, # 學期成績
        'c': None, # 學分資訊
        'y': None, # 學年成績
        'S': None, # 歷年學期成績
        'Y': None, # 歷年學年成績
        'r': None, # 重修科目
        'g': None, # 擔任幹部
        'C': None, # 社團
        'p': None, # 學期獎懲
        'P': None, # 歷年獎懲
        'n': None, # 學期缺曠
        "N": None, # 歷年缺曠
        'i': get_info
    }

    data = {}
    for i in mode:
        try:
            data[i] = mode_selector[i]()
        except KeyError:
            data[i] = {}
    return data