from src.dice import Dice
import matplotlib.pyplot as plt
from dataclasses import dataclass


# ------------------------------------------- #
#  Character / Faction model                  #
# ------------------------------------------- #
@dataclass
class Character:
    """ Data class that represents a character or faction """
    health: int = 0
    defense: int = 0
    attack_dice: Dice = 0
    damage_dice: Dice = 0
    n_attacks: int = 1

    @staticmethod
    def combine(*characters):
        """ Combine multiple characters into a single one """
        tot = Character(n_attacks=0)
        for ch in characters:
            tot.health += ch.health
            tot.defense += ch.defense * ch.health
            tot.n_attacks += ch.n_attacks
        tot.defense /= tot.health
        tot.defense = int(tot.defense)
        tot.attack_dice = Dice.combine(*[ch.attack_dice for ch in characters])
        tot.damage_dice = Dice.combine(*[ch.damage_dice for ch in characters])
        return tot

    def __str__(self):
        return f"Health:{self.health}, Defense: {self.defense}, Attack dice: {str(self.attack_dice)} " \
               f"Damage Dice: {str(self.damage_dice)}, No. Attacks: {self.n_attacks}"


# ------------------------------------------- #
#  Example                                    #
# ------------------------------------------- #
if __name__ == '__main__':
    c1 = Character(health=20, defense=11, attack_dice=Dice(1, 20, 0, 0),  damage_dice=Dice(1, 6, 0, 0))
    c2 = Character(health=30, defense=8,  attack_dice=Dice(1, 20, 2, -1), damage_dice=Dice(2, 6, 0, 0))
    c3 = Character(health=15, defense=14, attack_dice=Dice(1, 20, 3, 2),  damage_dice=Dice(2, 6, 2, 0))

    t = Character.combine(c1, c2, c3)
    print(t.health, t.defense)

    def plot_example(dice: Dice, title, target):
        fig, axs = plt.subplots(1,3, figsize=(20, 5))
        fig.suptitle(title, fontsize=18, fontweight='bold')
        axs[0].bar(dice.values, dice.distribution)
        axs[0].set_xticks(dice.values)
        axs[0].axvline(dice.avg, c='orange')
        axs[0].set_title('Distribution')
        axs[1].bar(dice.values, dice.cdf)
        axs[1].set_xticks(dice.values)
        axs[1].set_title('CDF')
        axs[2].bar(['F', 'T'], dice.prob_against(target))
        axs[2].set_title(f'Probability of rolling >= {target}')
        axs[2].set_ylim([0.0, 1.0])
        plt.show()

    plot_example(t.atk_dice, "a", t.defense)
    plot_example(t.dmg_dice, "a", t.defense)
