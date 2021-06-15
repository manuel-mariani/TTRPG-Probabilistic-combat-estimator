from dataclasses import dataclass
from typing import List
from src.aleatory_variable import AleatoryVariable
from src.character import Character
import matplotlib.pyplot as plt
from src.dice import Dice


# ------------------------------------------- #
#  Combat model / simulator                   #
# ------------------------------------------- #
class CombatModel:
    def __init__(self, a_character: Character, b_character: Character, max_rounds: int = 10):
        # Data initialization
        self.max_rounds = max_rounds
        self.rounds: List[RoundModel] = []
        self.round_number = 0

        # Initialize the round 0. No evidence is considered here
        self.rounds.append(RoundModel(
            a_hp=AleatoryVariable.from_exact(a_character.health, bounds=(0, a_character.health + 1)),
            b_hp=AleatoryVariable.from_exact(b_character.health, bounds=(0, b_character.health + 1))
        ))

        # Define the the constants used by the model, to be used if no evidence is provided
        self.__a_hits = AleatoryVariable.from_hit(a_character.attack_dice, b_character.defense)
        self.__b_hits = AleatoryVariable.from_hit(b_character.attack_dice, a_character.defense)
        self.__a_hits = self.__a_hits ** a_character.n_attacks
        self.__b_hits = self.__b_hits ** b_character.n_attacks

        self.__a_dmg = AleatoryVariable.from_dice(a_character.damage_dice)
        self.__b_dmg = AleatoryVariable.from_dice(b_character.damage_dice)

    # ------------------------------------------- #

    def advance_round(self, round_evidence):
        """ Advance the combat simulation from the current round, taking evidence if present"""
        prev_round = self.rounds[self.round_number]
        if round_evidence is None:
            round_evidence = RoundModel()

        # HITS
        a_hits = round_evidence.get('a_hits', self.__a_hits)
        b_hits = round_evidence.get('b_hits', self.__b_hits)

        # DAMAGE (dmg * hits)
        a_damage = round_evidence.get('a_damage', self.__a_dmg * a_hits)
        b_damage = round_evidence.get('b_damage', self.__b_dmg * b_hits)

        # HEALTH (hp_x(t-1) - damage_y(t))
        a_hp = round_evidence.get('a_hp', prev_round.a_hp - b_damage)
        b_hp = round_evidence.get('b_hp', prev_round.b_hp - a_damage)

        # Store the new round
        self.round_number += 1
        self.rounds.append(RoundModel(a_hp=a_hp,
                                      b_hp=b_hp,
                                      a_hits=a_hits,
                                      b_hits=b_hits,
                                      a_damage=a_damage,
                                      b_damage=b_damage
                                      ))

    # ------------------------------------------- #

    def simulate(self, evidence: dict = None):
        """ Simulate the entire encounter, advancing until the max number of rounds is reached"""
        evidence = {} if evidence is None else evidence
        for t in range(1, self.max_rounds):
            self.advance_round(evidence.get(self.round_number+1, None))

    # ------------------------------------------- #

    def plot_combat_history(self):
        """ Plot the entire combat history"""
        for r in range(len(self.rounds)):
            self.rounds[r].plot(r)
        plt.show()

    # ------------------------------------------- #


# ------------------------------------------- #
#  Round model / Evidence definition          #
# ------------------------------------------- #

@dataclass
class RoundModel:
    """
    Model of a round: hits, damage and hp of the two factions.
    It can be used as evidence for the combat model
    """
    a_hp: AleatoryVariable = None
    a_hits: AleatoryVariable = None
    a_damage: AleatoryVariable = None
    b_hp: AleatoryVariable = None
    b_hits: AleatoryVariable = None
    b_damage: AleatoryVariable = None

    # ------------------------------------------- #

    def get(self, attribute_name: str, default=None):
        """ Returns an attribute if present, else the default value provided (or none)"""
        val = getattr(self, attribute_name, default)
        return val if val is not None else default

    # ------------------------------------------- #

    def plot(self, round_no):
        """ Plots the round model """

        def _plot(axis, variable, title):
            axis.set_title(title)
            if variable is not None and isinstance(variable, AleatoryVariable):
                axis.bar(variable.domain, variable.distribution)

        # Figure init
        fig, axs = plt.subplots(2, 3)
        fig.tight_layout(rect=[0, 0.03, 1, 0.85])
        fig.suptitle(f"Round {round_no}")

        # Subplots
        _plot(axs[0, 0], self.a_hits, "Ally Hits")
        _plot(axs[0, 1], self.a_damage, "Ally Damage")
        _plot(axs[0, 2], self.a_hp, "Ally Health")
        _plot(axs[1, 0], self.b_hits, "Enemy Hits")
        _plot(axs[1, 1], self.b_damage, "Enemy Damage")
        _plot(axs[1, 2], self.b_hp, "Enemy Health")

    # ------------------------------------------- #


# ------------------------------------------- #
#  Example                                    #
# ------------------------------------------- #
if __name__ == '__main__':
    ally = Character(health=25, defense=15, attack_dice=Dice(1, 20), damage_dice=Dice(1, 6), n_attacks=3)
    enemy = Character(health=40, defense=8, attack_dice=Dice(1, 20), damage_dice=Dice(1, 6, 2), n_attacks=2)

    combat = CombatModel(ally, enemy)
    _evidence = {
        1: RoundModel(b_damage=AleatoryVariable.from_exact(6, bounds=(0, 6))),
        2: RoundModel(b_hp=AleatoryVariable.from_exact(20, bounds=(0, enemy.health))),
    }
    #combat.simulate()
    combat.simulate(_evidence)
    combat.plot_combat_history()
