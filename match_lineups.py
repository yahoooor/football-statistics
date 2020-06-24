import time
import unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from file_edit import *
from overall_match_info import OverallMatchInfo


class TeamFormation(OverallMatchInfo):

    def go_to_lineups(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "LINEUPS")))
        element.click()

    def _coaches(self):
        return self.driver.find_elements_by_class_name('hOBqth')

    def _coach_home(self):
        try:
            return self._coaches()[0].get_attribute('textContent')
        except IndexError:
            return '--'

    def _coach_away(self):
        try:
            return self._coaches()[1].get_attribute('textContent')
        except IndexError:
            return '--'

    def _home_formation_fields(self):  # goalkeeper, defender, midfield, (optionally sec midfield), forward)
        return self.driver.find_elements_by_class_name('iIjGro')

    def _away_formation_fields(self):
        return self.driver.find_elements_by_class_name('kKuJOw')

    def _substitutions_elem(self):
        subs = []
        elements = self.driver.find_elements_by_class_name('hZiwjT')
        for element in elements:
            if element.find_elements_by_class_name('glVCAK'):
                subs.append(element.find_element_by_xpath(".//*[name()='div' and @title]"))
        return subs

    @staticmethod
    def _team_formation(fields):
        formation = []
        for field in fields:
            players_in_field = len(field.find_elements_by_xpath(".//*[local-name()='img']"))
            formation.append(str(players_in_field))
        return '-'.join(formation)

    @staticmethod
    def _players_in_field(field):
        return field.find_elements_by_xpath(".//*[local-name()='div' and @title]")

    @staticmethod
    def _player_name(player):
        name = player.get_attribute('textContent')
        return unicodedata.normalize("NFKD", name)

    def _goalkeeper(self, fields):
        goalkeeper_field = fields[0]
        goalkeeper = self._players_in_field(goalkeeper_field)[0]
        return 'Goalkeeper', 'GK', self._player_name(goalkeeper)

    def _defenders(self, fields):
        defenders_field = fields[1]
        defenders_elem = self._players_in_field(defenders_field)
        defenders = []

        if len(defenders_elem) == 3:
            for defender in defenders_elem:
                defenders.append(('Defender', 'CB', self._player_name(defender)))

        elif len(defenders_elem) == 4:
            rb_elem = defenders_elem[0]
            rb = ('Defender', 'RB', self._player_name(rb_elem))
            cb2_elem = defenders_elem[1]
            cb2 = ('Defender', 'CB', self._player_name(cb2_elem))
            cb1_elem = defenders_elem[2]
            cb1 = ('Defender', 'CB', self._player_name(cb1_elem))
            lb_elem = defenders_elem[3]
            lb = ('Defender', 'LB', self._player_name(lb_elem))

            defenders.extend([lb, cb1, cb2, rb])

        elif len(defenders_elem) == 5:
            rb_elem = defenders_elem[0]
            rb = ('Defender', 'RB', self._player_name(rb_elem))
            cb3_elem = defenders_elem[1]
            cb3 = ('Defender', 'CB', self._player_name(cb3_elem))
            cb2_elem = defenders_elem[2]
            cb2 = ('Defender', 'CB', self._player_name(cb2_elem))
            cb1_elem = defenders_elem[3]
            cb1 = ('Defender', 'CB', self._player_name(cb1_elem))
            lb_elem = defenders_elem[4]
            lb = ('Defender', 'LB', self._player_name(lb_elem))

            defenders.extend([lb, cb1, cb2, cb3, rb])
        return defenders

    def _midfielders(self, fields):
        midfielders = []

        if len(fields) == 4:
            midfielders_field = fields[2]
            midfielders_elem = self._players_in_field(midfielders_field)

            if len(midfielders_elem) == 3:
                for midfielder in midfielders_elem:
                    midfielders.append(('Midfielder', 'CM', self._player_name(midfielder)))

            elif len(midfielders_elem) == 4:
                rm_elem = midfielders_elem[0]
                rm = ('Midfielder', 'RM', self._player_name(rm_elem))
                cm2_elem = midfielders_elem[1]
                cm2 = ('Midfielder', 'CM', self._player_name(cm2_elem))
                cm1_elem = midfielders_elem[2]
                cm1 = ('Midfielder', 'CM', self._player_name(cm1_elem))
                lm_elem = midfielders_elem[3]
                lm = ('Midfielder', 'LM', self._player_name(lm_elem))

                midfielders.extend([lm, cm1, cm2, rm])

            else:  # 5 midfielders
                rwb_elem = midfielders_elem[0]
                rwb = ('Midfielder', 'RWB', self._player_name(rwb_elem))
                cm3_elem = midfielders_elem[1]
                cm3 = ('Midfielder', 'CM', self._player_name(cm3_elem))
                cm2_elem = midfielders_elem[2]
                cm2 = ('Midfielder', 'CM', self._player_name(cm2_elem))
                cm1_elem = midfielders_elem[3]
                cm1 = ('Midfielder', 'CM', self._player_name(cm1_elem))
                lwb_elem = midfielders_elem[4]
                lwb = ('Midfielder', 'LWB', self._player_name(lwb_elem))

                midfielders.extend([lwb, cm1, cm2, cm3, rwb])

        elif len(fields) == 5:
            def_midfielders_field = fields[2]
            def_midfielders_elem = self._players_in_field(def_midfielders_field)

            midfielders_field = fields[3]
            midfielders_elem = self._players_in_field(midfielders_field)

            if len(def_midfielders_elem) < 4:
                for def_midfielder in def_midfielders_elem:
                    midfielders.append(('Midfielder', 'DM', self._player_name(def_midfielder)))
            elif len(def_midfielders_elem) == 4:
                rwb_elem = def_midfielders_elem[0]
                rwb = ('Midfielder', 'RWB', self._player_name(rwb_elem))
                dm2_elem = def_midfielders_elem[1]
                dm2 = ('Midfielder', 'DM', self._player_name(dm2_elem))
                dm1_elem = def_midfielders_elem[2]
                dm1 = ('Midfielder', 'DM', self._player_name(dm1_elem))
                lwb_elem = def_midfielders_elem[3]
                lwb = ('Midfielder', 'LWB', self._player_name(lwb_elem))

                midfielders.extend([lwb, dm1, dm2, rwb])
            else:
                rwb_elem = def_midfielders_elem[0]
                rwb = ('Midfielder', 'RWB', self._player_name(rwb_elem))
                dm3_elem = def_midfielders_elem[1]
                dm3 = ('Midfielder', 'DM', self._player_name(dm3_elem))
                dm2_elem = def_midfielders_elem[2]
                dm2 = ('Midfielder', 'DM', self._player_name(dm2_elem))
                dm1_elem = def_midfielders_elem[3]
                dm1 = ('Midfielder', 'DM', self._player_name(dm1_elem))
                lwb_elem = def_midfielders_elem[4]
                lwb = ('Midfielder', 'LWB', self._player_name(lwb_elem))

                midfielders.extend([lwb, dm1, dm2, dm3, rwb])

            if len(midfielders_elem) < 3:
                for midfielder in midfielders_elem:
                    midfielders.append(('Midfielder', 'CAM', self._player_name(midfielder)))

            elif len(midfielders_elem) == 3:
                rm_elem = midfielders_elem[0]
                rm = ('Midfielder', 'RM', self._player_name(rm_elem))
                cam_elem = midfielders_elem[1]
                cam = ('Midfielder', 'CAM', self._player_name(cam_elem))
                lm_elem = midfielders_elem[2]
                lm = ('Midfielder', 'LM', self._player_name(lm_elem))

                midfielders.extend([lm, cam, rm])

            elif len(midfielders_elem) == 4:
                rm_elem = midfielders_elem[0]
                rm = ('Midfielder', 'RM', self._player_name(rm_elem))
                cm2_elem = midfielders_elem[1]
                cm2 = ('Midfielder', 'CM', self._player_name(cm2_elem))
                cm1_elem = midfielders_elem[2]
                cm1 = ('Midfielder', 'CM', self._player_name(cm1_elem))
                lm_elem = midfielders_elem[3]
                lm = ('Midfielder', 'LM', self._player_name(lm_elem))

                midfielders.extend([lm, cm1, cm2, rm])
        return midfielders

    def _forwards(self, fields):
        if len(fields) == 4:
            forwards_field = fields[3]
        else:
            forwards_field = fields[4]
        forwards_elem = self._players_in_field(forwards_field)
        forwards = []

        if len(forwards) < 3:
            for forward in forwards_elem:
                forwards.append(('Forward', 'CF', self._player_name(forward)))

        elif len(forwards) == 3:
            rw_elem = forwards_elem[0]
            rw = ('Midfielder', 'RW', self._player_name(rw_elem))
            cf_elem = forwards_elem[1]
            cf = ('Midfielder', 'CF', self._player_name(cf_elem))
            lw_elem = forwards_elem[3]
            lw = ('Midfielder', 'LW', self._player_name(lw_elem))

            forwards.extend([lw, cf, rw])
        return forwards

    def _substitutions(self):
        subs = self._substitutions_elem()
        substitutions = []
        for sub in subs:
            sub_name = unicodedata.normalize("NFKD", sub.get_attribute('title'))
            substitutions.append(('Substitution', '--', sub_name))
        return substitutions

    @staticmethod
    def _count_subs(formation_fields):
        subs_counter = 0
        for field in formation_fields:
            subs = len(field.find_elements_by_class_name('kobsPn'))
            subs_counter = subs_counter + subs
        return subs_counter

    def _substitutions_home(self):
        home_subs = self._count_subs(self._home_formation_fields())
        away_subs = self._count_subs(self._away_formation_fields())
        all_subs = len(self._substitutions())
        if home_subs < away_subs:
            diff = all_subs - home_subs - away_subs
        else:
            diff = 0
        return self._substitutions()[:home_subs + diff]

    def _substitutions_away(self):
        home_subs = self._count_subs(self._home_formation_fields())
        away_subs = self._count_subs(self._away_formation_fields())
        all_subs = len(self._substitutions())
        if home_subs < away_subs:
            diff = all_subs - home_subs - away_subs
        else:
            diff = 0
        return self._substitutions()[home_subs + diff:]

    def _team_formation_players(self, team):
        players = [self._goalkeeper(team)]
        players.extend([*self._defenders(team),
                        *self._midfielders(team),
                        *self._forwards(team)])
        return players

    def _home_formation_players(self):
        return self._team_formation_players(self._home_formation_fields())

    def _away_formation_players(self):
        return self._team_formation_players(self._away_formation_fields())


    def _formation_to_file(self, formation_fields, team_name, driver_number):

        if team_name == self._home_team():
            coach = self._coach_home()
            formation = self._team_formation(formation_fields)
        else:
            coach = self._coach_away()
            formation = self._team_formation(formation_fields)

        filename = '{}/league/formations.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()
            basic_info = {
                'Team': team_name,
                'Home/Away': self._home_away(team_name),
                'Opponent': self._opponent(team_name),
                'Date': date,
                'Coach': coach,
                'Formation': formation
            }

            writer(file, filename, header_added, basic_info)
        file.close()

    @logger('formations')
    def both_formations_to_file(self, driver_number):
        self._formation_to_file(self._home_formation_fields(), self._home_team(), driver_number)
        time.sleep(0.25)
        self._formation_to_file(self._away_formation_fields(), self._away_team(), driver_number)

    def _all_team_players(self, team):
        if team == self._home_team():
            return [*self._home_formation_players(), *self._substitutions_home()]
        else:
            return [*self._away_formation_players(), *self._substitutions_away()]

    def _formation_players_to_file(self, players, team_name , driver_number):
        filename = '{}/league/formations_players.csv'.format(driver_number)
        header_added = False
        with codecs.open(filename, 'a', 'utf-8') as file:
            date = self._match_date()
            print(team_name)
            for player in players:
                player_name = player[2]
                position = player[1]
                position_type = player[0]

                basic_info = {
                    'Player name': player_name,
                    'Team': team_name,
                    'Opponent': self._opponent(team_name),
                    'Position type': position_type,
                    'Position': position,
                    'Date': date
                }

                writer(file, filename, header_added, basic_info)
                header_added = True
        file.close()

    @logger('formation players')
    def both_formation_players_to_file(self, driver_number):
        home_team = self._home_team()
        away_team = self._away_team()
        self._formation_players_to_file(self._all_team_players(home_team), home_team, driver_number)
        self._formation_players_to_file(self._all_team_players(away_team), away_team, driver_number)
