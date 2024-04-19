import requests
import bs4
import re
from sqlighter import SQLighter
import encode


class Lesson():
    def __init__(self, title, info):
        self.time = title[0].text
        self.title = title[2].text
        self.type = info.select('.lesson__params > .lesson__type')[0].text
        if info.select('.lesson__params > .lesson__teachers'):
            self.teacher = info.select('.lesson__params > .lesson__teachers')[0].text[1:]
        else:
            self.teacher = 'Данные о преподавателе отсутсвуют'
        if info.select('.lesson__params > .lesson__places'):
            self.place = info.select('.lesson__params > .lesson__places')[0].text
        else:
            self.place = 'Место не уточнено'


def bold(text):
    return "*" + text + "*"


def italic(text):
    return "_" + text + "_"


def universities():
    # Get universities dictionary
    r = requests.get('https://ruz.spbstu.ru/')
    html = bs4.BeautifulSoup(r.content, 'html.parser')
    all_unvesities = html.select('.faculty-list__list > .faculty-list__item')
    all_links = html.select('.faculty-list__list > .faculty-list__item > .faculty-list__link')
    return {name.text: 'https://ruz.spbstu.ru' + ''.join(re.findall(r'href="(.*)"', str(link))) for name, link in zip(all_unvesities, all_links)}


def groups(url):
    # Get groups dictionary
    r = requests.get(url)
    html = bs4.BeautifulSoup(r.content, 'html.parser')
    all_groups = html.select('.groups-list > .groups-list__item > .groups-list__link')
    return {link.text: 'https://ruz.spbstu.ru' + ''.join(re.findall(r'href="(.*)"', str(link))) for link in
            all_groups}


def need_to_switch(day, id):
    if day + 1 > db.get_days_number(id):
        return 1
    if day < 0:
        return -1
    return 0


def init_parse(id, schedule_url, day):
    global msg_title
    r = requests.get(schedule_url)
    html = bs4.BeautifulSoup(r.content, 'html.parser')
    week = html.select('.schedule > .schedule__day')
    msg = ""
    for days in week:
        msg += '🗓' + bold('Расписание на ' + days.select('.schedule__date')[0].text) + '\n\n'
        for k, el in enumerate(days.select('.schedule__lessons > .lesson')):
            title = el.select('.lesson__subject > span')
            lesson = Lesson(title, el)
            msg += '🕐' + bold(lesson.time) + ' ' + bold(lesson.title) + '\n' + '🏫' + italic(lesson.type) + '\n' + \
                   '👨‍🏫' + italic(lesson.teacher) + '\n' + '🏡' + bold(lesson.place) + \
                   '\n\n' * int(k != len(days.select('.schedule__lessons > .lesson')) - 1)
        msg += "newday"

    db.update_days_number(id, len(week))
    db.update_encoded(id, 'encoded_week', encode.encode(msg))
    print(msg)
    return msg.split('newday')[day]


def parse_week(id, day):
    if need_to_switch(day, id) == 1:
        day = 0
        db.update_days_number(id, len(encode.decode(db.get_encoded(id, 'encoded_next_week')).split("newday")))
        return [encode.decode(db.get_encoded(id, 'encoded_next_week')).split("newday")[day], 1]

    elif need_to_switch(day, id) == -1:
        days_number = len(encode.decode(db.get_encoded(id, 'encoded_prev_week')).split("newday"))
        day = days_number - 1
        db.update_days_number(id, days_number)
        return [encode.decode(db.get_encoded(id, 'encoded_prev_week')).split("newday")[day], -1]
    return [encode.decode(db.get_encoded(id, 'encoded_week')).split("newday")[day], 0]


def update_week_urls(id, schedule_url):
    # Schedule parsing
    r = requests.get(schedule_url)
    html = bs4.BeautifulSoup(r.content, 'html.parser')

    week_select = [''.join(re.findall(r'date=\d\d\d\d-\d{1,2}-\d{1,2}',
                                      str(s))) for s in html.select('.switcher > div > a')]
    week_select = list(set(filter(lambda x: x != '', week_select)))
    week_select.sort(key=lambda x: list(map(lambda y: [int(k) for k in y],
                                            re.findall(r'(\d\d\d\d)-(\d{1,2})-(\d{1,2})', x))))
    index = schedule_url.index('?')
    for i, week_name in enumerate(['prev_week_url', 'next_week_url']):
        schedule_url = schedule_url[:index + 1] + week_select[i]
        db.update_link(id, week_name, schedule_url)


def update_encoded_week(id):
    for i, week_name in enumerate(['prev_week_url', 'week_url', 'next_week_url']):
        schedule_url = db.get_link(id, week_name)
        r = requests.get(schedule_url)
        html = bs4.BeautifulSoup(r.content, 'html.parser')
        week = html.select('.schedule > .schedule__day')
        msg = ""
        for days in week:
            msg += '🗓' + bold('Расписание на ' + days.select('.schedule__date')[0].text) + '\n\n'
            for k, el in enumerate(days.select('.schedule__lessons > .lesson')):
                title = el.select('.lesson__subject > span')
                lesson = Lesson(title, el)
                msg += '🕐' + bold(lesson.time) + ' ' + bold(lesson.title) + '\n' + '🏫' + italic(lesson.type) + '\n' + \
                       '👨‍🏫' + italic(lesson.teacher) + '\n' + '🏡' + bold(lesson.place) + \
                       '\n\n' * int(k != len(days.select('.schedule__lessons > .lesson')) - 1)
            msg += "newday"
        db.update_encoded(id, 'encoded_'+week_name[:-4], encode.encode(msg))
        db.update_days_number(id, len(msg.split('newday')))
        print(msg)

# Base initialisation
db = SQLighter('telegrambot_database_new.db')

# Title for schedule
msg_title = ('''
╔═╗─────╔══╗─╔╗───╔╗
║╬╠═╦╗╔╦╣══╬═╣╚╦═╦╝╠╦╦╗╔═╗
║╔╣╬║╚╣║╠══║═╣║║╩╣╬║║║╚╣╩╣
╚╝╚═╩═╬╗╠══╩═╩╩╩═╩═╩═╩═╩═╝
──────╚═╝  ''')
