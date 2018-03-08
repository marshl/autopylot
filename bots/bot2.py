from game_state import GameState, FleetCommand
import random


def get_commands(game_state: GameState):
    if not game_state.get_enemy_planet_count() or not game_state.get_my_planet_count():
        return []

    for neutral in game_state.get_neutral_planets():
        for mine in game_state.get_my_planets():
            if mine.ships >= neutral.ships + 2:
                return [FleetCommand(mine.planet_id, neutral.planet_id, neutral.ships + 1)]

    for enemy in game_state.get_enemy_planets():
        for mine in game_state.get_my_planets():
            if mine.ships >= enemy.ships + 2:
                return [FleetCommand(mine.planet_id, enemy.planet_id, enemy.ships + 1)]

    return []
