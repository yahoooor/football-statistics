import time
from selenium.common.exceptions import NoSuchElementException
from overall_match_info import OverallMatchInfo
from file_edit import *


class HeatMap(OverallMatchInfo):

    def _bars(self):
        return self.driver.find_elements_by_xpath("//*[name()='g'][@*[name()='class' and .='bars-group']]"
                                                  "/*[name()='rect']")

    def _heat_map(self):
        height = self._bars()
        color = self._bars()
        heat_map = []

        for h, c in zip(height, color):
            h = h.get_attribute('height')
            c = c.get_attribute('fill')
            if c == '#52b030' or c == 'rgb(82, 176, 48)':
                heat_map.append((h, 'HOME'))
            else:
                heat_map.append((h, 'AWAY'))
        return heat_map

    @logger('heatmaps')
    def heat_map_to_file(self, driver_number):
        filename = '{}/league/heatmaps.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            basic_info = {
                'Home': self._home_team(),
                'Away': self._away_team(),
                'Date': self._match_date(),
                'League': self._league(),
                'Heatmap': self._heat_map()
            }

            writer(file, filename, header_added, basic_info)
        file.close()


class MatchActions(OverallMatchInfo):

    def _home_match_actions(self):
        return self.driver.find_elements_by_class_name("hjvBju")

    def _away_match_actions(self):
        return self.driver.find_elements_by_class_name("dOZkvi")

    @staticmethod
    def _filter_action(filter_name, match_actions):
        filtered_action = []
        for action in match_actions:
            kind = action.find_elements_by_xpath(".//*[local-name()='svg']/*[local-name()='title']")
            if kind:
                kind_name = kind[0].get_attribute('textContent')
                if kind_name in filter_name:
                    filtered_action.append(action)
        return filtered_action


class Cards(MatchActions):

    def _filter_cards(self, match_actions):
        cards = ['Yellow card', '2nd Yellow card (Red)', 'Red card']
        return self._filter_action(cards, match_actions)

    def _filter_cards_home(self):
        return self._filter_cards(self._home_match_actions())

    def _filter_cards_away(self):
        return self._filter_cards(self._away_match_actions())

    def _cards_to_file(self, cards, team, driver_number):
        filename = '{}/league/cards.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()
            opponent = self._opponent(team)
            referee = self._referee()

            if cards:
                for card in cards:
                    kind = card.find_element_by_xpath(".//*[local-name()='svg']/*[local-name()='title']").get_attribute(
                        'textContent')
                    player = card.find_element_by_xpath(".//a[@class='u-txt']").get_attribute('textContent')
                    minute = card.find_element_by_xpath(".//*[local-name()='span']").get_attribute('textContent')
                    if len(card.find_elements_by_class_name('gPjuve')) != 0:
                        reason = card.find_element_by_class_name('gPjuve').get_attribute('textContent')
                    else:
                        reason = '--'

                    card_pattern = {
                        'Player': player,
                        'Kind': kind,
                        'Date': date,
                        'Minute': minute,
                        'Opponent': opponent,
                        'Reason': reason,
                        'Referee': referee,
                        'Team': team

                    }

                    writer(file, filename, header_added, card_pattern)
                    header_added = True
        file.close()

    def _home_cards_to_file(self, driver_number):
        self._cards_to_file(self._filter_cards_home(), self._home_team(), driver_number)

    def _away_cards_to_file(self, driver_number):
        self._cards_to_file(self._filter_cards_away(), self._away_team(), driver_number)

    @logger('cards')
    def cards_to_file_both(self, driver_number):
        self._home_cards_to_file(driver_number)
        time.sleep(0.25)
        self._away_cards_to_file(driver_number)


class Goals(MatchActions):

    def _filter_goals(self, match_actions):
        goals = ['Goal', 'Penalty', 'goal.ownGoal', 'Missed Penalty']
        return self._filter_action(goals, match_actions)

    def _filter_goals_home(self):
        return self._filter_goals(self._home_match_actions())

    def _filter_goals_away(self):
        return self._filter_goals(self._away_match_actions())

    def _goals_to_file(self, goals, team, driver_number):
        filename = '{}/league/goals.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()

            if goals:
                for goal in goals:
                    kind = goal.find_element_by_xpath(".//*[local-name()='svg']/*[local-name()='title']").get_attribute(
                        'textContent')
                    scorer = goal.find_element_by_xpath(".//a[@class='u-txt']").get_attribute('textContent')
                    try:
                        assist = goal.find_element_by_xpath(".//a[@class='u-txt-2']").get_attribute('textContent')
                        assist = assist.lstrip('Assist: ')
                    except NoSuchElementException:
                        assist = 'No assist'
                    minute = goal.find_element_by_xpath(".//*[local-name()='span']").get_attribute('textContent')

                    if not kind == 'goal.ownGoal':
                        opponent = self._opponent(team)

                    else:
                        opponent = self._opponent(self._opponent(team))

                    goal_pattern = {
                        'Scorer': scorer,
                        'Assist': assist,
                        'Kind': kind,
                        'Minute': minute,
                        'Opponent': opponent,
                        'Date': date,
                        'Team': team
                    }
                    writer(file, filename, header_added, goal_pattern)
                    header_added = True
        file.close()

    def _home_goals_to_file(self, driver_number):
        self._goals_to_file(self._filter_goals_home(), self._home_team(), driver_number)

    def _away_goals_to_file(self, driver_number):
        self._goals_to_file(self._filter_goals_away(), self._away_team(), driver_number)

    @logger('goals')
    def goals_to_file_both(self, driver_number) :
        self._home_goals_to_file(driver_number)
        time.sleep(0.25)
        self._away_goals_to_file(driver_number)


class VarDecision(MatchActions):

    def _filter_vars(self, match_actions):
        var = 'VAR decision'
        return self._filter_action(var, match_actions)

    def _filter_vars_home(self):
        return self._filter_vars(self._home_match_actions())

    def _filter_vars_away(self):
        return self._filter_vars(self._away_match_actions())

    def _vars_to_file(self, var_decisions, team, driver_number):
        filename = '{}/league/vars.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()

            if var_decisions:
                for var in var_decisions:
                    kind = var.find_element_by_xpath(".//*[local-name()='svg']/*[local-name()='title']").get_attribute(
                        'textContent')
                    which_player = var.find_element_by_xpath(".//a[@class='u-txt']").get_attribute('textContent')\
                        .strip('()')
                    # try:
                    #     assist = var.find_element_by_xpath(".//a[@class='u-txt-2']").get_attribute('textContent')
                    #     assist = assist.lstrip('Assist: ')
                    # except NoSuchElementException:
                    #     assist = 'No assist'
                    var_full_name = var.find_element_by_class_name('QcNtO').text
                    decision = var.find_elements_by_class_name('gYsVZh')[1].get_attribute('textContent')\
                        .replace(var_full_name, '').replace(which_player, '').rstrip()

                    minute = var.find_element_by_xpath(".//*[local-name()='span']").get_attribute('textContent')

                    var_pattern = {
                        'Player': which_player,
                        'Kind': kind,
                        'Decision': decision,
                        'Var type': var_full_name,
                        'Minute': minute,
                        'Opponent': self._opponent(team),
                        'Date': date,
                        'Team': team
                    }
                    writer(file, filename, header_added, var_pattern)
                    header_added = True
        file.close()

    def _home_vars_to_file(self, driver_number):
        self._vars_to_file(self._filter_vars_home(), self._home_team(), driver_number)

    def _away_vars_to_file(self, driver_number):
        self._vars_to_file(self._filter_vars_away(), self._away_team(), driver_number)

    @logger('vars')
    def vars_to_file_both(self, driver_number):
        self._home_vars_to_file(driver_number)
        time.sleep(0.25)
        self._away_vars_to_file(driver_number)
