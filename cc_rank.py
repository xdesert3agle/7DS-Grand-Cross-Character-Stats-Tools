import argh
import requests
import ast
import math
from bs4 import BeautifulSoup
import pandas as pd
import const

class Database:
    url = 'https://gamewith.jp/7taizai/article/show/158813'
    rows = ''
    char_names = ''
    characters = []
    characters_dict = []

    def fetch_html(self):
        try:
            request = requests.get(self.url)
            request.raise_for_status()

            soup = BeautifulSoup(request.content, 'html.parser')
            self.rows = soup.select('.w-toggle-section[data-toggle-value="1"] table.sorttable tr:not(:first-child)')

        except requests.exceptions.HTTPError as errh:
            print(f"Error HTTP: {errh}")

        except requests.exceptions.ConnectionError as errc:
            print(f"Error al conectar: {errc}")

        except requests.exceptions.Timeout as errt:
            print(f"Timeout: {errt}")

        except requests.exceptions.RequestException as err:
            print(f"Error: {err}")
        
        

    def fetch_jp_translated_char_names(self):
        with open(const.UNITS_FILENAME, "r", encoding="utf8") as f:
            self.char_names = ast.literal_eval(f.read())

    def fetch_data(self):
        for row in db.rows:
            name = row['data-col1']
            hp = row['data-col2']
            attack = row['data-col3']
            defense = row['data-col4']
            cc = row['data-col5']

            c = Character(
                self.translate_name(name),
                int(cc.replace(',', '')),
                int(attack.replace(',', '')),
                int(defense.replace(',', '')),
                int(hp.replace(',', '')))
            
            self.characters.append(c)
            self.characters_dict.append(vars(c))
    
    def translate_name(self, name):
        return self.char_names[name]
    
    def get_character(self, name):
        return [x for x in self.characters if x.name == name][0]

    def get_sorted_data(self, param):
        index_name = {'name': 'name', 'cc': 'cc', 'atk': 'attack', 'def': 'defense', 'hp': 'hp'}
        sorted_data = sorted(self.characters_dict, key=lambda dict: dict[index_name[param]], reverse=True)

        return pd.DataFrame(sorted_data).to_string()


class Character:
    COSMETIC_MAX_WEAPON_BASE_ATK_INCREASE = 210
    COSMETIC_MAX_ARMOR_BASE_DEF_INCREASE = 210
    COSMETIC_MAX_HAIR_BASE_HP_INCREASE = 1650

    EQUIP_UR_BRACE_BASE_ATK = 1640
    EQUIP_UR_RING_BASE_ATK = 840
    EQUIP_UR_NECKLACE_BASE_DEF = 820
    EQUIP_UR_EARRINGS_BASE_DEF = 420
    EQUIP_UR_BELT_BASE_HP = 16400
    EQUIP_UR_RUNE_BASE_HP = 8400

    EQUIP_PERFECT_ROLLS_STAT_INCREASE = 30
    STAT_INCREASING_SET_STAT_INCREASE = 20

    def __init__(self, name='', cc='', attack='', defense='', hp=''):
        self.name = name
        self.cc = cc
        self.attack = attack
        self.defense = defense
        self.hp = hp
    
    def get_max_stats(self):
        
        # Estad??sticas base m??ximas (sin equipamiento)
        max_base_atk = (self.attack
            + (self.COSMETIC_MAX_WEAPON_BASE_ATK_INCREASE * 5)
            + self.EQUIP_UR_BRACE_BASE_ATK
            + self.EQUIP_UR_RING_BASE_ATK)

        max_base_def = (self.defense
            + (self.COSMETIC_MAX_ARMOR_BASE_DEF_INCREASE * 5)
            + self.EQUIP_UR_NECKLACE_BASE_DEF
            + self.EQUIP_UR_EARRINGS_BASE_DEF)

        max_base_hp = (self.hp
            + (self.COSMETIC_MAX_HAIR_BASE_HP_INCREASE * 5)
            + self.EQUIP_UR_BELT_BASE_HP
            + self.EQUIP_UR_RUNE_BASE_HP)

        # Se computa el equipamiento (con y sin set que boostee la estad??stica)
        max_boosted_atk = int(math.ceil(max_base_atk * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE + self.STAT_INCREASING_SET_STAT_INCREASE) / 100)))
        max_boosted_def = int(math.ceil(max_base_def * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE + self.STAT_INCREASING_SET_STAT_INCREASE) / 100)))
        max_boosted_hp = int(math.ceil(max_base_hp * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE + self.STAT_INCREASING_SET_STAT_INCREASE) / 100)))
        max_non_boosted_atk = int(math.ceil(max_base_atk * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE) / 100)))
        max_non_boosted_def = int(math.ceil(max_base_def * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE) / 100)))
        max_non_boosted_hp = int(math.ceil(max_base_hp * ((100 + self.EQUIP_PERFECT_ROLLS_STAT_INCREASE) / 100)))

        print(f'\nATK + DEF:\n ?? ATK:\t{max_boosted_atk:,}\n ?? DEF:\t{max_boosted_def:,}\n ?? HP:\t{max_non_boosted_hp:,}\n'.replace(',', '.'))
        print(f'ATK + CD:\n ?? ATK:\t{max_boosted_atk:,}\n ?? DEF:\t{max_non_boosted_def:,}\n ?? HP:\t{max_non_boosted_hp:,}\n'.replace(',', '.'))
        print(f'HP + DEF:\n ?? ATK:\t{max_non_boosted_atk:,}\n ?? DEF:\t{max_boosted_def:,}\n ?? HP:\t{max_boosted_hp:,}'.replace(',', '.'))


# Argh commands
def show_ranking(order='cc'):
    print(db.get_sorted_data(order))

def max_stats(character_name):
    character = db.get_character(character_name)
    character.get_max_stats()


# Main code
db = Database()
db.fetch_html()
db.fetch_jp_translated_char_names()
db.fetch_data()

parser = argh.ArghParser()
parser.add_commands([show_ranking, max_stats])

if __name__ == '__main__':
    parser.dispatch()