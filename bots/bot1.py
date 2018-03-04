from autopylot import GameState, FleetCommand


def get_commands(game_state: GameState):
    home_planet = game_state.get_my_planets()[0]
    enemy_planet = game_state.get_enemy_planets()[0]

    if home_planet.ships > 1:
        return [FleetCommand(home_planet.planet_id, enemy_planet.planet_id, 1)]

    return []
