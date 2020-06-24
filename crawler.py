import threading

from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from distutils.dir_util import copy_tree

from match_player_stats import PlayerStats
from match_statistics import TeamMatchStatistics
from match_details import *

# PATH = path to webdriver 
chrome_options = Options()
chrome_options.add_argument('--lang=en')


class CrawlLinks(OverallMatchInfo):

    @staticmethod
    def __get_match_time(match):
        time_exists = len(match.find_elements_by_class_name('cOCEtm'))
        match_time = '--'
        if time_exists:
            match_time = match.find_element_by_class_name('cOCEtm').get_attribute('textContent')
        return match_time

    @staticmethod
    def __get_match_date(match):
        return match.find_element_by_class_name('gYsVZh').get_attribute('textContent')

    def _get_matches_links(self, league):
        matches = self.driver.find_elements_by_class_name('dhKVQJ')
        with open('matches_links/matches_links_{}.txt'.format(league), 'a') as f:
            for match in matches:
                match_time = self.__get_match_time(match)
                match_date = self.__get_match_date(match)
                link = match.get_attribute('href')
                curr_date = str(datetime.date.today().strftime('%d/%m/%y'))
                if ':' in match_date:
                    match_time = match_date
                    match_date = curr_date

                f.write(link + ' ' + match_date + ' ' + match_time + '\n')
        f.close()

    def _prev_next_buttons(self):
        return self.driver.find_elements_by_class_name('epVTwK')

    def _prev_next_matchday(self, prev_next):
        if len(self._prev_next_buttons()) != 1:
            self._prev_next_buttons()[prev_next].click()
            time.sleep(0.1)
            return True
        else:
            return False

    def crawl_for_match_links(self, league):
        round_number = int(self._round().split(' ')[1])
        print(round_number)
        start_crawling = False
        if round_number > 19:
            start_end = 1
        else:
            start_end = 0
        while True:
            if not self._prev_next_matchday(start_end):
                break
        while True:
            self._get_matches_links(league)
            if not start_crawling:
                self._prev_next_buttons()[abs(start_end - 1)].click()
                time.sleep(0.1)
                self._get_matches_links(league)
                start_crawling = True
            if not self._prev_next_matchday(abs(start_end - 1)):
                break


class CrawlMatch(TeamMatchStatistics, Cards, Goals, HeatMap, VarDecision, PlayerStats):

    def _details_crawl(self, driver_number):
        time.sleep(1)
        self.heat_map_to_file(driver_number)
        self.vars_to_file_both(driver_number)
        self.goals_to_file_both(driver_number)
        self.cards_to_file_both(driver_number)

    def _statistics_crawl(self, driver_number):
        self.both_team_stats_to_file('full-time', driver_number)
        time.sleep(0.5)
        self.go_to_1st_half()
        self.both_team_stats_to_file('1st half', driver_number)
        time.sleep(0.5)
        self.go_to_2nd_half()
        self.both_team_stats_to_file('2nd half', driver_number)

    def _lineups_crawl(self, driver_number):
        time.sleep(0.5)
        self.both_formation_players_to_file(driver_number)
        self.both_formations_to_file(driver_number)
        self.all_players_stats_to_file(driver_number)

    def match_crawl(self, driver_number):
        self._details_crawl(driver_number)
        self._statistics_crawl(driver_number)
        self._lineups_crawl(driver_number)


class CrawlAvailableMatches(CrawlMatch):

    def _h2h_matches(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.visibility_of(self.driver.find_elements_by_class_name('fxQxZC')[1]))
        return self.driver.find_elements_by_class_name('fxQxZC')[1].find_elements_by_class_name('gRmngh')

    @staticmethod
    def _h2h_match_date(match):
        return match.find_element_by_class_name('gYsVZh').get_attribute('textContent')

    @staticmethod
    def _convert_date(date):
        return datetime.datetime.strptime(date, '%d/%m/%y').strftime('%Y-%m-%d')

    @staticmethod
    def _matches_per_driver(driver_number):
        with open('./matches_links/matches_{}.txt'.format(driver_number)) as f:
            for line in f.readlines():
                line_split = line.split(' ')
                match_link = line_split[0]
                match_date = parse(str(datetime.datetime.strptime(line_split[1], '%d/%m/%y'))).date()

                match_time = line_split[2]
                curr_date = parse(str(datetime.date.today())).date()
                # curr_time = datetime.datetime.now().strftime('%H:%M')
                if curr_date > match_date and match_time != '--':
                    # with open('visited.txt', 'r') as v:
                    #     if line not in v:
                    yield line

    def matches(self, driver_number):
        for match in self._matches_per_driver(driver_number):
            print(match)
            copy_tree("{}/league".format(driver_number), "{}/backup".format(driver_number))  # backup
            match_split = match.split(' ')
            match_link = match_split[0]
            match_date = match_split[1]
            self.driver.get(match_link)

            time.sleep(3)
            h2h = self._h2h_matches()
            h2h_last_match = self._h2h_match_date(h2h[0])

            if match_date == h2h_last_match:
                print('Its ok')
                self.match_crawl(driver_number)
            else:
                print('Choosing proper match')
                for m in h2h:
                    h2h_date = self._h2h_match_date(m)
                    if h2h_date == match_date:
                        ActionChains(self.driver).move_to_element_with_offset(m, 8, 8).click().perform()
                        time.sleep(4)
                        self.match_crawl(driver_number)
                        if str(self._match_date()) != str(self._convert_date(match_date)):  # make sure dates are proper
                            print('dates are not correct')
                            exit(0)
            with open('./matches_links/visited_{}.txt'.format(driver_number), 'a') as f:
                f.write(match)
            f.close()


def main(driver_number):
    driver3 = webdriver.Chrome(executable_path=PATH, options=chrome_options)
    c = CrawlAvailableMatches(driver3)
    c.matches(driver_number)
    return


if __name__ == '__main__':
    threads = 6
    split_links_into_threads(threads)
    for i in range(threads):
        initialize_folders(i)
        threading.Thread(target=main, args=[i]).start()
        time.sleep(10)

