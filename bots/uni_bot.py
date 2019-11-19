from game_state import GameState, FleetCommand
import math
import random


def get_planet_plus_fleets(game_state: GameState, planet_id: int):
    return (
        game_state.get_planet(planet_id).ships
        + sum(
            [
                fleet.ships
                for fleet in game_state.get_enemy_fleets()
                if fleet.destination_planet == planet_id
            ]
        )
        - sum(
            [
                fleet.ships
                for fleet in game_state.get_my_fleets()
                if fleet.destination_planet == planet_id
            ]
        )
    )


def get_commands(game_state: GameState):
    source_planet = max(game_state.get_my_planets(), key=lambda p: p.ships)

    if not source_planet:
        return

    if (
        len(game_state.get_enemy_planets()) == 0
        and len(game_state.get_enemy_fleets()) > 0
    ):
        return [
            FleetCommand(
                source_planet.planet_id,
                enemy_fleet.destination_planet,
                source_planet.ships / 2,
            )
            for source_planet in game_state.get_my_planets()
            for enemy_fleet in game_state.get_enemy_fleets()
        ]

    if len(game_state.get_my_planets()) / 2 > len(game_state.get_enemy_planets()):

        commands = []
        enemy_planets = game_state.get_enemy_planets()

        for idx, my_planet in enumerate(game_state.get_my_planets()):
            enemy_planet = enemy_planets[idx % len(enemy_planets)]
            cmd = FleetCommand(
                my_planet.planet_id, enemy_planet.planet_id, my_planet.ships / 2
            )
            commands.append(cmd)
        return commands

    best_score = -math.inf
    target_planet = None
    for planet in game_state.get_enemy_planets() + game_state.get_neutral_planets():
        if planet is source_planet:
            return

        score = 0
        if (
            planet.ships > 0
            and planet.player_id != game_state.current_player
            and get_planet_plus_fleets(game_state, planet.planet_id) > 0
        ):
            dist = game_state.get_trip_length(source_planet.planet_id, planet.planet_id)
            score = planet.ship_growth / (planet.ships * dist)

        if (
            planet.player_id == game_state.current_player
            and get_planet_plus_fleets(game_state, planet.planet_id) < 0
        ):
            dist = game_state.get_trip_length(source_planet.planet_id, planet.planet_id)
            score = planet.ship_growth * 10 / dist

        if score > best_score:
            best_score = score
            target_planet = planet

    if target_planet is None:
        return

    num_ships = get_planet_plus_fleets(game_state, source_planet.planet_id) / 2
    target_num_ships = get_planet_plus_fleets(game_state, target_planet.planet_id)

    if num_ships > target_num_ships:
        if target_planet.player_id == 0:
            return FleetCommand(
                source_planet.planet_id, target_planet.planet_id, target_num_ships + 10
            )

        if target_planet.player_id != game_state.current_player:
            dist = game_state.get_trip_length(
                source_planet.planet_id, target_planet.planet_id
            )
            return FleetCommand(
                source_planet.planet_id,
                target_planet.planet_id,
                target_num_ships + target_planet.ship_growth * dist + 10,
            )

        if target_planet.player_id == game_state.current_player:
            return FleetCommand(
                source_planet.planet_id, target_planet.planet_id, target_num_ships + 10
            )

    return []
