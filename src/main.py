from src.character import Character
from src.dice import Dice
from src.simulator import CombatModel

if __name__ == '__main__':
    # Allies
    a1 = Character(health=29, defense=15, attack_dice=Dice(1, 20, 2), damage_dice=Dice(1, 6, 1))
    a2 = Character(health=19, defense=15, attack_dice=Dice(1, 20, 3), damage_dice=Dice(2, 6))
    a3 = Character(health=32, defense=14, attack_dice=Dice(1, 20, 1), damage_dice=Dice(1, 6, 2))
    a4 = Character(health=37, defense=13, attack_dice=Dice(1, 20, 2, -1), damage_dice=Dice(3, 6, 1))
    a5 = Character(health=31, defense=13, attack_dice=Dice(1, 20, 3, 1), damage_dice=Dice(1, 6))

    # Enemies
    e1 = Character(health=37, defense=14, attack_dice=Dice(1, 20, 4, 1), damage_dice=Dice(2, 6), n_attacks=2)
    e2 = e1
    e3 = Character(health=12, defense=13, attack_dice=Dice(1, 20, 5, 1), damage_dice=Dice(1, 6))
    e4 = e3

    # Faction definition
    allies = Character.combine(a1, a2, a3, a4, a5)
    enemies = Character.combine(e1, e2, e3, e4)

    # Combat simulation
    combat = CombatModel(allies, enemies)
    combat.simulate()
    combat.plot_combat_history()
