import requests
from pyquery import PyQuery as pq
import pandas as pd
isnan = lambda x:x!=x
valid = lambda x:x if not isnan(x) else ''

def get(account=None, password=None, mode='i'):
    if not(account and password):
        raise ValueError('Account or password Error!')
    s = requests.Session()
    s.encoding = 'big5'

    login = s.post("http://academic.hchs.hc.edu.tw/skyweb/main.asp", data={
        "txtid":account,
        "txtpwd":password,
        "check":"confirm"}) # Login
    login.encoding = 'big5'
    if "帳號或密碼錯誤" in login.text:
        raise ValueError('Account or password Error!')
    login = s.get("http://academic.hchs.hc.edu.tw/skyweb/f_left.asp")

    def get_score(): # 學期成績
        get_score_data = s.get("http://academic.hchs.hc.edu.tw/skyweb/stu/stu_result9.asp")
        get_score_data.encoding = 'big5'
        score_data = pd.read_html(get_score_data.text)[2] # score table
        subjects = [i for i in score_data[0]] # 包合總分之類的
        score = {}
        for i in range(4,score_data.shape[1],4):
            score[score_data[i][0]] = dict(zip(score_data[0][1:subjects.index("總分")],
            [[valid(score_data[i][j]), 
            valid(score_data[i+1][j]), 
            score_data[i+2][j] + '/' + score_data[i+3][j] if not (isnan(score_data[i+2][j] or isnan(score_data[i+3][j]))) else '', 
            '',
            ''] for j in range(1,subjects.index("總分"))]))
        for key in score:
            for i in range(subjects.index("總分"), subjects.index("總分")+7):
                score[key][score_data[0][i]] = valid(score_data[list(score.keys()).index(key)+1][i])
        """
        資料格式: {'第1次平時成績':
                    {'◎ 國文Ⅴ':[ 成績 , 平均 , 排名 , 類組排, 校排],
                    '◎ 英文Ⅴ': ['78', '', '', '', ''],
                    ....,
                    '總分': ''....},
                ....}
        }}
        """
        return score

    
    def get_info():
        get_infos = s.get('http://academic.hchs.hc.edu.tw/skyweb/stu/stu_data_qr.asp#a2')
        get_infos.encoding = 'big5'
        infos = pd.read_html(get_infos.text)[2]
        infos = {
            'studentId': valid(infos[1][1]),
            'name': valid(infos[3][1]),
            'class': valid(infos[3][2])
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