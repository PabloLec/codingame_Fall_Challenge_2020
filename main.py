import sys
from itertools import permutations
from pickle import dumps

NUMBER_OF_TURNS = 2
LAST_BEST_COMBINATION = None
CURRENT_INDEX = 0

POTIONS = []
INVENTORY = {}

SEEN_COMBINATIONS = []
COMBINATIONS = {0: []}
BEST_COMBINATION = None
MONTY_PYTHON = ["Now, what do burn besides witches?", "More witches!"]


class Potion:
    def __init__(self):
        self.action_id = None
        self.action_type = None
        self.delta_0 = None
        self.delta_1 = None
        self.delta_2 = None
        self.delta_3 = None
        self.price = None
        self.tome_index = None
        self.tax_count = None
        self.castable = None
        self.repeatable = None

    def __eq__(self, other):
        return (
            dumps(self) == dumps(other) if isinstance(other, Potion) else NotImplemented
        )


def get_combinations():  # sourcery skip: avoid-builtin-shadow
    global SEEN_COMBINATIONS
    global COMBINATIONS

    all = list(permutations(POTIONS, NUMBER_OF_TURNS))
    log(f"{len(all)} permutations")
    for combination in all:
        if combination in SEEN_COMBINATIONS:
            continue
        SEEN_COMBINATIONS.append(combination)
        price = 0
        temp_inventory = INVENTORY.copy()

        for potion in combination:
            if not is_potion_doable(potion, temp_inventory):
                break
            do_potion(potion, temp_inventory)
            price += potion.price

        if price in COMBINATIONS:
            COMBINATIONS[price].append(combination)
        else:
            COMBINATIONS[price] = [combination]

    log(f"COMBINATIONS: {COMBINATIONS.keys()}")


def find_best_combination():
    global BEST_COMBINATION

    best = sorted(COMBINATIONS.keys(), reverse=True)
    for combination_list in best:
        sorted_list = sorted(COMBINATIONS[combination_list], key=len)
        for combination in sorted_list:
            if is_combination_doable(combination):
                log(f"best combination: {combination}")
                BEST_COMBINATION = combination
                return


def is_potion_doable(potion, inventory=None):
    if inventory is None:
        inventory = INVENTORY

    if abs(potion.delta_0) > inventory[0]["inv_0"]:
        return False
    if abs(potion.delta_1) > inventory[0]["inv_1"]:
        return False
    if abs(potion.delta_2) > inventory[0]["inv_2"]:
        return False
    if abs(potion.delta_3) > inventory[0]["inv_3"]:
        return False

    return True


def is_combination_doable(combination, index=0):
    return all(is_potion_in_list(p, POTIONS) for p in combination[index:])


def do_potion(potion, inventory):
    inventory[0]["inv_0"] += potion.delta_0
    inventory[0]["inv_1"] += potion.delta_1
    inventory[0]["inv_2"] += potion.delta_2
    inventory[0]["inv_3"] += potion.delta_3


def is_potion_in_list(potion, iterable):
    return any(potion == p for p in iterable)


def remove_expired_potions(this_turn_potions):
    global POTIONS
    for p in POTIONS:
        if not is_potion_in_list(p, this_turn_potions):
            POTIONS.remove(p)


def log(text):
    print(text, file=sys.stderr, flush=True)


def get_vars():
    global POTIONS, INVENTORY

    POTIONS = []
    action_count = int(input())  # the number of spells and recipes in play
    this_turn_potions = []
    for _ in range(action_count):
        potion = Potion()
        inputs = input().split()
        potion.action_id = int(inputs[0])  # the unique ID of this spell or recipe
        potion.action_type = inputs[
            1
        ]  # in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
        potion.delta_0 = int(inputs[2])  # tier-0 ingredient change
        potion.delta_1 = int(inputs[3])  # tier-1 ingredient change
        potion.delta_2 = int(inputs[4])  # tier-2 ingredient change
        potion.delta_3 = int(inputs[5])  # tier-3 ingredient change
        potion.price = int(inputs[6])  # the price in rupees if this is a potion
        potion.tome_index = int(
            inputs[7]
        )  # in the first two leagues: always 0; later: the index in the tome if this is a tome spell, equal to the read-ahead tax; For brews, this is the value of the current urgency bonus
        potion.tax_count = int(
            inputs[8]
        )  # in the first two leagues: always 0; later: the amount of taxed tier-0 ingredients you gain from learning this spell; For brews, this is how many times you can still gain an urgency bonus
        potion.castable = (
            inputs[9] != "0"
        )  # in the first league: always 0; later: 1 if this is a castable player spell
        potion.repeatable = (
            inputs[10] != "0"
        )  # for the first two leagues: always 0; later: 1 if this is a repeatable player spell

        if not is_potion_in_list(potion, POTIONS):
            POTIONS.append(potion)
        this_turn_potions.append(potion)

    INVENTORY = {}
    for i in range(2):
        # inv_0: tier-0 ingredients in inventory
        # score: amount of rupees
        INVENTORY[i] = {}
        (
            INVENTORY[i]["inv_0"],
            INVENTORY[i]["inv_1"],
            INVENTORY[i]["inv_2"],
            INVENTORY[i]["inv_3"],
            INVENTORY[i]["score"],
        ) = [int(j) for j in input().split()]

    remove_expired_potions(this_turn_potions)


def main_loop(turn):
    global LAST_BEST_COMBINATION, CURRENT_INDEX

    get_vars()

    get_combinations()
    if turn == 0 or not is_combination_doable(BEST_COMBINATION, CURRENT_INDEX):
        find_best_combination()
    log(f"Current best: {BEST_COMBINATION}")
    combination_index = (
        0 if BEST_COMBINATION != LAST_BEST_COMBINATION else CURRENT_INDEX
    )
    next_potion = BEST_COMBINATION[combination_index]
    print(f"BREW {next_potion.action_id}", MONTY_PYTHON[turn])
    if LAST_BEST_COMBINATION == BEST_COMBINATION:
        CURRENT_INDEX += 1
    else:
        CURRENT_INDEX = 0
        LAST_BEST_COMBINATION = BEST_COMBINATION


turn = 0
# game loop
while True:
    main_loop(turn)
    turn += 1
