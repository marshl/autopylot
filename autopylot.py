import math

import tkinter as tk


class Fleet:
    def __init__(self, ships: int, player: int, source_planet: int, destination_planet: int, total_trip_length: int):
        self.ships = ships
        self.player = player
        self.source_planet = source_planet
        self.destination_planet = destination_planet

        self.total_trip_length = total_trip_length
        self.turns_remaining = total_trip_length

    def get_turns_travelled(self):
        return self.turns_remaining - self.total_trip_length


class Planet:
    def __init__(self, planet_id: int, x_pos: float, y_pos: float, player: int, ships: int, ship_growth: int):
        self.planet_id = planet_id
        self.x_pos, self.y_pos = x_pos, y_pos
        self.player = player
        self.ships = ships
        self.ship_growth = ship_growth


class GameController:
    def __init__(self):
        self.game_state = GameState()

    def load_map_file(self, map_file: str):
        planet_id = 1
        with open(map_file, 'r') as f:
            for line in f:
                affix, x_pos, y_pos, player, ships, ship_growth = line.split(' ')
                x_pos, y_pos = float(x_pos), float(y_pos)
                player, ships, ship_growth = int(player), int(ships), int(ship_growth)
                planet = Planet(planet_id, x_pos, y_pos, player, ships, ship_growth)
                self.game_state.planets.append(planet)
                planet_id += 1

    def get_extents(self):
        min_x = min([planet.x_pos for planet in self.game_state.get_planets()])
        max_x = max([planet.x_pos for planet in self.game_state.get_planets()])
        min_y = min([planet.y_pos for planet in self.game_state.get_planets()])
        max_y = max([planet.y_pos for planet in self.game_state.get_planets()])

        return (min_x, max_x), (min_y, max_y)

    def turn_step(self):
        for fleet in self.game_state.fleets:
            fleet.turns_remaining -= 1
            if fleet.turns_remaining <= 0:
                self.land_fleet(fleet)

        for planet in self.game_state.planets:
            if planet.player != 0:
                planet.ships += planet.ship_growth

    def land_fleet(self, fleet: Fleet):
        planet = self.game_state.get_planet_by_id(fleet.destination_planet)
        if fleet.player == planet.player:
            planet.ships += fleet.ships
        else:
            planet.ships -= fleet.ships
            if planet.ships < 0:
                planet.ships *= -1
                planet.player = planet

        self.game_state.fleets.remove(fleet)

    def launch_fleet(self, source_planet: Planet, destination_planet: Planet, ships: int):
        if ships <= 0:
            raise ValueError('Can only launch a positive number of ships')

        if source_planet.ships - ships <= 0:
            raise ValueError('Cannot launch more ships than are on a planet')

        source_planet.ships -= ships
        distance = self.get_trip_length(source_planet, destination_planet)
        fleet = Fleet(ships, source_planet.player, source_planet.planet_id, destination_planet.planet_id, distance)
        self.game_state.fleets.append(fleet)

    def get_trip_length(self, source_planet: Planet, destination_planet: Planet):
        x_dist = source_planet.x_pos - destination_planet.x_pos
        y_dist = source_planet.y_pos - destination_planet.y_pos
        return int(math.sqrt(x_dist ** 2 + y_dist ** 2))

    def process_command(self, source_planet_id: int, target_planet_id: int, ships: int):
        source_planet = self.game_state.get_planet_by_id(source_planet_id)
        target_planet = self.game_state.get_planet_by_id(target_planet_id)
        self.launch_fleet(source_planet, target_planet, ships)


class GameState:
    def __init__(self):
        self.planets = list()
        self.fleets = list()

    def get_planet_by_id(self, planet_id: int):
        return next((planet for planet in self.planets if planet.id == planet_id), None)

    def get_planets(self):
        return self.planets

    def get_my_planets(self):
        return self.get_player_planets(1)

    def get_enemy_planets(self):
        return self.get_player_planets(2)

    def get_neutral_planets(self):
        return self.get_player_planets(0)

    def get_player_planets(self, player: int):
        if player not in [0, 1, 2]:
            raise ValueError('Cannot get planets for players other than 0,1,2')

        return [planet for planet in self.planets if planet.player == player]

    def get_fleets(self):
        return self.fleets

    def get_my_fleets(self):
        return self.get_player_fleets(1)

    def get_enemy_fleets(self):
        return self.get_player_fleets(2)

    def get_player_fleets(self, player: int):
        if player not in [1, 2]:
            raise ValueError('Can only get fleets for players 1 and 2')

        return [fleet for fleet in self.fleets if fleet.player == player]

    def get_player_is_alive(self, player: int):
        return self.get_player_planets(player) or self.get_player_planets(player)


if __name__ == '__main__':
    controller = GameController()
    controller.load_map_file('maps/map1.txt')
    (min_x, max_x), (min_y, max_y) = controller.get_extents()

    root = tk.Tk()
    tk.Button(root, text='Hello, world!').grid()
    root.mainloop()
