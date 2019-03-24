from game_state import GameState, FleetCommand
import math
import random


def get_planet_plus_fleets(game_state: GameState, planet_id: int):
    return game_state.get_planet(planet_id).ships + \
           sum([fleet.ships for fleet in game_state.get_enemy_fleets() if
                fleet.destination_planet == planet_id]) - \
           sum([fleet.ships for fleet in game_state.get_my_fleets() if
                fleet.destination_planet == planet_id])


def get_commands(game_state: GameState):
    for fleet in game_state.get_enemy_fleets():
        target = game_state.get_planet(fleet.destination_planet)
        # if targeting my planet
        if target.player == game_state.current_player:
            pass

    return []
