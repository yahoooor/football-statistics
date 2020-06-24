import time
import dateutil.parser as parser


class Driver:
    def __init__(self, driver):
        self.driver = driver


class OverallMatchInfo(Driver):

    def _match_date(self):
        string_date = self.driver.find_element_by_class_name('gkEvHG').get_attribute('textContent').split(' ')
        extract = string_date[2] + ' ' + string_date[3] + ' ' + string_date[4]
        parsed_date = parser.parse(extract).date()
        return parsed_date

    def _home_team(self):
        return self.driver.find_element_by_class_name("AlZbs").get_attribute('textContent').split(' - ')[0]

    def _away_team(self):
        return self.driver.find_element_by_class_name("AlZbs").get_attribute('textContent').split(' - ')[1]

    def _opponent(self, team):
        is_away = team == self._away_team()
        return self._home_team() if is_away else self._away_team()

    def _home_away(self, team):
        return 'H' if team == self._home_team() else 'A'

    def _referee(self):
        time.sleep(0.25)
        info_box = self.driver.find_elements_by_css_selector('.gkEvHG')
        return info_box[2].get_attribute('textContent').lstrip("Referee: ").split(',')[0]

    def _league(self):
        return self.driver.find_element_by_class_name('cGRfjB') \
            .find_elements_by_xpath(".//*[name()='li']")[2].get_attribute('textContent')

    def _round(self):
        matchday_number = self.driver.find_element_by_class_name('lhzbZg').find_elements_by_tag_name('li')[1] \
            .get_attribute('textContent').split(', ')[1]
        return matchday_number

    def _scoreboard(self):
        return self.driver.find_elements_by_class_name('bjFVmy')[0].get_attribute('textContent').split(' - ')

    def _goals_scored(self, team):

        is_home = team == self._home_team()
        goals = self._scoreboard()
        return goals[0] if is_home else goals[1]

    def _goals_conceded(self, team):
        is_home = team == self._home_team()
        goals = self._scoreboard()
        return goals[1] if is_home else goals[0]

    def _total_goals(self, team):
        return int(self._goals_scored(team)) + int(self._goals_conceded(team))

    def _final_result(self, team):
        scored = int(self._goals_scored(team))
        conceded = int(self._goals_conceded(team))
        if scored > conceded:
            return 'Win'
        elif conceded > scored:
            return 'Lose'
        else:
            return 'Draw'

    def _scoreboard_halftime(self):
        board = self.driver.find_element_by_class_name('kKUrfO')
        return board.find_elements_by_xpath(".//*[local-name()='div' and @style]")[0].get_attribute('textContent') \
            .strip('()').split(' - ')

    def _goals_scored_halftime(self, team):
        is_home = team == self._home_team()
        goals = self._scoreboard_halftime()
        return goals[0] if is_home else goals[1]

    def _goals_conceded_halftime(self, team):
        is_home = team == self._home_team()
        goals = self._scoreboard_halftime()
        return goals[1] if is_home else goals[0]

    def _total_goals_halftime(self, team):
        return int(self._goals_scored_halftime(team)) + int(self._goals_conceded_halftime(team))

    def _halftime_result(self, team):
        scored = int(self._goals_scored_halftime(team))
        conceded = int(self._goals_conceded_halftime(team))
        if scored > conceded:
            return 'Win'
        elif conceded < scored:
            return 'Lose'
        else:
            return 'Draw'
