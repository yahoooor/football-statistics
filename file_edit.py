import codecs
import datetime
import os
from csv import DictWriter
import pathlib
from glob import glob
from dateutil.parser import parse


def file_empty(filename):
    return os.stat(filename).st_size == 0


def writer(file, filename, header_added, dictionary):
    keys = dictionary.keys()
    dict_writer = DictWriter(file, keys, delimiter=";")
    if not header_added and file_empty(filename):
        dict_writer.writeheader()
    dict_writer.writerow(dictionary)


def add_match_log(*args):
    with codecs.open('./logs/logs.txt', 'a', 'utf-8') as log:
        log.write('{}'.format(args))
    log.close()


def logger(title):
    def inner(func):
        def wrapper(*args):
            func(*args)
            add_match_log('got {}'.format(title))
        return wrapper
    return inner


def initialize_folders(driver):
    pathlib.Path('./{}/league/'.format(driver)).mkdir(parents=True, exist_ok=True)
    # a = ['cards', 'formations', 'goals', 'heatmaps', 'players', 'teams', 'vars']
    # p_sub = ['goalkeepers', 'players']
    # t_sub = ['1st half', '2nd half', 'full-time']
    # for main in a:
    #     pathlib.Path('./{}/league/{}'.format(driver, main)).mkdir(parents=True, exist_ok=True)
    # for p in p_sub:
    #     pathlib.Path('./{}/league/players/{}'.format(driver, p)).mkdir(parents=True, exist_ok=True)
    # for t in t_sub:
    #     pathlib.Path('./{}/league/teams/{}'.format(driver, t)).mkdir(parents=True, exist_ok=True)


def finished_matches():
    with open('links.txt') as f:
        for line in f.readlines():
            line_split = line.split(' ')
            match_link = line_split[0]
            match_date = parse(str(datetime.datetime.strptime(line_split[1], '%d/%m/%y'))).date()

            match_time = line_split[2]
            curr_date = parse(str(datetime.date.today())).date()
            if curr_date > match_date and match_time != '--':
                with open('visited.txt', 'r') as v:
                    if line not in v:
                        yield line


def split_links_into_threads(threads):
    for index, match in enumerate(finished_matches()):
        thread = index % threads
        with open('matches_{}.txt'.format(thread), 'a') as f:
            f.write(match)


def combine_details():
    dirs = ['cards', 'heatmaps', 'formations', 'formations_players', 'goals', 'vars', 'players', 'goalkeepers',
            '1st half', '2nd half', 'full-time']
    for d in dirs:
        csv = []
        header = ''
        paths = glob('./drivers/*/league/{}.csv'.format(d))
        for p in paths:
            with codecs.open(p, 'r', 'utf-8') as f2:
                for index, line in enumerate(f2.readlines()):
                    if index == 0:
                        header = line
                    else:
                        csv.append(line)
        with codecs.open('./logs/final/{}'.format('{}.csv'.format(d)), 'a', 'utf-8') as f3:
            f3.write(header)
            f3.write(''.join(csv))

