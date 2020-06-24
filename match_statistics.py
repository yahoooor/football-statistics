from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_edit import *
from overall_match_info import OverallMatchInfo
from dictonary_patterns import team_stats_pattern
import time


class TeamMatchStatistics(OverallMatchInfo):

    def _get_all_stats(self):
        return self.driver.find_elements_by_class_name('StatisticsStyles__StatisticsItemContent-zf4n59-1')

    def _home_stats(self):
        home = self._get_all_stats()[::3]
        return dict(zip(self._stats_titles(), home))

    def _away_stats(self):
        away = self._get_all_stats()[2::3]
        return dict(zip(self._stats_titles(), away))

    def _stats_titles(self):
        return self._get_all_stats()[1::3]

    def _team_avg_rating(self, team):
        if team == self._home_team():
            return self.driver.find_element_by_class_name('cVVUpH')\
                .find_element_by_class_name('styles__Rating-r1pe6j-0').get_attribute('textContent')
        else:
            return self.driver.find_element_by_class_name('hNZyvh')\
                .find_element_by_class_name('styles__Rating-r1pe6j-0').get_attribute('textContent')

    def _team_stats_to_file(self, team, stats, first_second_full, driver_number):
        filename = '{}/league/{}.csv'.format(driver_number, first_second_full)
        header_added = False
        pattern_dict = team_stats_pattern()
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()
            basic_info = {
                'Opponent': self._opponent(team),
                'Home/Away': self._home_away(team),
                'Goals scored': self._goals_scored(team),
                'Goals conceded': self._goals_conceded(team),
                'Total goals': self._total_goals(team),
                'Date': date,
                'Result': self._final_result(team),
                'Half-time scored': self._goals_scored_halftime(team),
                'Half-time conceded': self._goals_conceded_halftime(team),
                'Half-time result': self._halftime_result(team),
                'Team name': team,
                'Referee': self._referee(),
                'League': self._league(),
                'Average rating': self._team_avg_rating(team)
            }
            pattern_dict.update(basic_info)

            for title, stat in stats.items():
                stat = stat.get_attribute('textContent')
                title = title.get_attribute('textContent')
                pattern_dict[title] = stat

            writer(file, filename, header_added, pattern_dict)
        file.close()

    def go_to_stats(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'STATISTICS')))
        element.click()

    def go_to_1st_half(self):
        self.driver.find_element_by_link_text('1ST').click()

    def go_to_2nd_half(self):
        self.driver.find_element_by_link_text('2ND').click()

    def _team_stats_home_to_file(self, first_second_full, driver_number):
        self._team_stats_to_file(self._home_team(), self._home_stats(), first_second_full, driver_number)

    def _team_stats_away_to_file(self, first_second_full, driver_number):
        self._team_stats_to_file(self._away_team(), self._away_stats(), first_second_full, driver_number)

    @logger_stats
    def both_team_stats_to_file(self, first_second_full, driver_number):
        time.sleep(0.5)
        self._team_stats_home_to_file(first_second_full, driver_number)
        time.sleep(0.25)
        self._team_stats_away_to_file(first_second_full, driver_number)
