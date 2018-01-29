import requests
from pyquery import PyQuery as pq
import pandas as pd
import math

def get(account=None, password=None, mode='s'):
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
        score = {}
        for i in range(4,33,4):
            score[score_data[i][0]] = dict(zip(score_data[0][1:15],
            [[score_data[i][j], score_data[i+1][j], score_data[i+2][j], score_data[i+3][j]] for j in range(1,15)]))
        for key in score:
            for i in range(15,22):
                score[key][score_data[0][i]] = score_data[list(score.keys()).index(key)+1][i]
        """
        資料格式: {'第1次平時成績':
                    {'◎ 國文Ⅴ':[ 成績 , 平均 , 排名 , 排名人數],
                    '◎ 英文Ⅴ': ['78', nan, nan, nan],
                    ....,
                    '總分': nan....},
                ....}
        }}
        """
        return score

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
        "N": None # 歷年缺曠
    }
    data = {}
    for i in mode:
        try:
            data[i] = mode_selector[i]()
        except KeyError:
            data[i] = {}
    return data