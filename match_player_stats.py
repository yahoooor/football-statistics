import codecs
import time
import unicodedata
from dictonary_patterns import goalkeeper_pattern, player_pattern
from file_edit import writer, logger
from match_lineups import TeamFormation


class PlayerStats(TeamFormation):

    def _players_rows(self):
        return self.driver.find_element_by_class_name('dygnyR').find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

    @staticmethod
    def _name(player):
        return player.find_element_by_class_name('cZNSgf').get_attribute('textContent')

    @staticmethod
    def _player_rating(player):
        return player.find_element_by_class_name('jtaVpb').get_attribute('textContent')

    @staticmethod
    def _stats_in_row(player):
        return player.find_elements_by_class_name('hTKZks')

    def _player_stats_titles(self):
        return self.driver.find_element_by_class_name('dygnyR').find_element_by_tag_name('thead') \
                   .find_elements_by_tag_name('th')[2:-1]

    def _stats_buttons(self):
        return self.driver.find_elements_by_class_name('bpUSvK')[2].find_elements_by_class_name('bfqsCw')

    def _home_away_logos(self, team):
        logos = self.driver.find_elements_by_class_name('ewBQSh')
        if team == self._home_team():
            logos[0].click()
        else:
            logos[1].click()

    @staticmethod
    def _notes_to_title_stat(stat):
        remove_digits = str.maketrans('', '', '123456789')
        titles_no_digits = stat.translate(remove_digits)
        import re
        notes_stats = list(zip(titles_no_digits.split(': '), re.findall(r'\d+', stat)))
        return notes_stats

    def _player_stats(self, team, driver_number):
        player_list = {}
        all_players = self._all_team_players(team)
        print(all_players)
        for p in all_players:  # initialize home or away players
            if p[0] == 'Goalkeeper':
                player_list[p[2]] = goalkeeper_pattern()
            else:
                player_list[p[2]] = player_pattern()

        self.driver.find_element_by_link_text('PLAYER STATISTICS').click()
        time.sleep(1)
        self._home_away_logos(team)  # go to player stats and choose home or away

        def player_stats_to_file():

            stats_buttons = self._stats_buttons()
            for stat_button in stats_buttons:  
                time.sleep(1)
                stat_button.click()
                players = self._players_rows()
                for player in players:  
                    titles = self._player_stats_titles()
                    stats = self._stats_in_row(player)
                    rating = self._player_rating(player)

                    name = self._name(player)
                    player_name = unicodedata.normalize("NFKD", name)
                    basic_info = {
                        'Player': player_name,
                        'Opponent': self._opponent(team),
                        'Home/Away': self._home_away(team),
                        'Date': self._match_date(),
                        'Result': self._final_result(team),
                        'Team name': team,
                        'Referee': self._referee(),
                    }
                    player_list[player_name].update(basic_info)

                    for t, s in zip(titles, stats):  # each stat for player
                        title = t.get_attribute('textContent')
                        stat = s.get_attribute('textContent')
                        if title == 'Notes':
                            if stat != '-':
                                notes_stats = self._notes_to_title_stat(stat)
                                for note in notes_stats:  # split notes to stats
                                    player_list[player_name][note[0]] = note[1]
                        else:
                            player_list[player_name][title] = stat
                            player_list[player_name]['Rating'] = rating
            self._player_stats_to_file(player_list, team, driver_number)
            self.driver.find_element_by_link_text('LINEUPS').click()
            time.sleep(3)
        return player_stats_to_file()

    @staticmethod
    def _player_stats_to_file(player_list, team, driver_number):
        for player, stats in player_list.items():
            if player_list[player]['Position'] == 'G':
                filename = '{}/league/goalkeepers.csv'.format(driver_number)
            else:
                filename = '{}/league/players.csv'.format(driver_number)

            header_added = False
            with codecs.open(filename, 'a', 'utf-8') as file:
                writer(file, filename, header_added, player_list[player])
            file.close()

    @logger('player stats')
    def all_players_stats_to_file(self, driver_number):
        self._player_stats(self._home_team(), driver_number)
        self._player_stats(self._away_team(), driver_number)



