from game_state import GameState, FleetCommand
import random


def get_commands(game_state: GameState):
    if not game_state.get_enemy_planet_count() or not game_state.get_my_planet_count():
        return []

    home_planet = random.choice(game_state.get_my_planets())
    target_planet = random.choice(game_state.get_planets())

    if home_planet == target_planet:
        return []

    if home_planet.ships > 1:
        return [
            FleetCommand(
                home_planet.planet_id,
                target_planet.planet_id,
                random.randrange(1, home_planet.ships),
            )
        ]

    return []
