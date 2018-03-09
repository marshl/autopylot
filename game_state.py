import copy
import importlib
import math


class Bot:
    def __init__(self, filename: str):
        self.player_id = None
        self.filename = filename
        self.name = self.module_name = self.filename.replace('.py', '')
        self.module = None

    def __str__(self):
        return f'Bot:{self.name}:{self.player_id}'

    def reload_module(self):
        if not self.module:
            self.module = importlib.import_module('bots.' + self.module_name)
        else:
            self.module = importlib.reload(self.module)

    def get_module(self):
        if not self.module:
            self.reload_module()

        return self.module


class Fleet:
    def __init__(self, ships: int, player_id: int, source_planet: int, destination_planet: int, total_trip_length: int):
        self.ships = ships
        self.player_id = player_id
        self.source_planet = source_planet
        self.destination_planet = destination_planet

        self.total_trip_length = total_trip_length
        self.turns_remaining = total_trip_length

    def __str__(self):
        return f'Fleet:{self.fleet_id}'

    def get_turns_travelled(self):
        return self.total_trip_length - self.turns_remaining


class Planet:
    def __init__(self, planet_id: int, x_pos: float, y_pos: float, player_id: int, ships: int, ship_growth: int):
        self.planet_id = planet_id
        self.x_pos, self.y_pos = x_pos, y_pos
        self.player_id = player_id
        self.ships = ships
        self.ship_growth = ship_growth

    def __str__(self):
        return f'Planet:{self.planet_id}'


class FleetCommand:
    def __init__(self, source_planet: int, destination_planet: int, ships: int):
        self.source_planet = source_planet
        self.destination_planet = destination_planet
        self.ships = ships


class GameController:
    def __init__(self):
        self.bot_1 = self.bot_2 = None
        self.turn_count = 0
        self.game_state = None
        self.selected_map = None

    def start_game(self, bot_1: Bot, bot_2: Bot):
        self.bot_1 = bot_1
        self.bot_1.player_id = 1
        self.bot_2 = bot_2
        self.bot_2.player_id = 2
        self.game_state = GameState()
        self.turn_count = 0

    def get_player_bot(self, player_id: int):
        if player_id == 1:
            return self.bot_1
        elif player_id == 2:
            return self.bot_2


    def copy_game_state(self, current_player: int):
        state = copy.deepcopy(self.game_state)
        state.current_player = current_player
        state.enemy_player = 2 if current_player == 1 else 1
        return state

    def load_map_file(self, map_file: str):
        planet_id = 1
        with open(map_file, 'r') as f:
            for line in f:
                affix, x_pos, y_pos, player_id, ships, ship_growth = line.split(' ')
                x_pos, y_pos = float(x_pos), float(y_pos)
                player_id, ships, ship_growth = int(player_id), int(ships), int(ship_growth)
                planet = Planet(planet_id, x_pos, y_pos, player_id, ships, ship_growth)
                self.game_state.planets.append(planet)
                planet_id += 1
        self.selected_map = map_file

    def get_extents(self):
        min_x = min([planet.x_pos for planet in self.game_state.get_planets()])
        max_x = max([planet.x_pos for planet in self.game_state.get_planets()])
        min_y = min([planet.y_pos for planet in self.game_state.get_planets()])
        max_y = max([planet.y_pos for planet in self.game_state.get_planets()])

        return (min_x, max_x), (min_y, max_y)

    def turn_step(self):

        self.turn_count += 1

        bot_1_commands = self.bot_1.get_module().get_commands(self.copy_game_state(1))
        bot_2_commands = self.bot_2.get_module().get_commands(self.copy_game_state(2))

        if bot_1_commands:
            for command in bot_1_commands:
                self.process_command(command, 1)

        if bot_2_commands:
            for command in bot_2_commands:
                self.process_command(command, 2)

        for fleet in self.game_state.fleets:
            fleet.turns_remaining -= 1
            if fleet.turns_remaining <= 0:
                self.land_fleet(fleet)

        self.game_state.fleets = [fleet for fleet in self.game_state.fleets if fleet.turns_remaining > 0]

        for planet in self.game_state.planets:
            if planet.player_id != 0:
                planet.ships += planet.ship_growth

    def land_fleet(self, fleet: Fleet):
        planet = self.game_state.get_planet(fleet.destination_planet)
        if fleet.player_id == planet.player_id:
            planet.ships += fleet.ships
        else:
            planet.ships -= fleet.ships
            if planet.ships < 0:
                planet.ships *= -1
                planet.player_id = fleet.player_id

    def launch_fleet(self, source_planet: Planet, destination_planet: Planet, ships: int):
        if ships <= 0:
            raise ValueError('Can only launch a positive number of ships')

        if source_planet.ships - ships <= 0:
            raise ValueError(
                f'Player {source_planet.player_id} tried to launch {ships} ships from {source_planet} '
                f'(has only {source_planet.ships} ships)')

        source_planet.ships -= ships
        distance = self.get_trip_length(source_planet, destination_planet)
        fleet = Fleet(ships, source_planet.player_id, source_planet.planet_id, destination_planet.planet_id, distance)
        fleet.fleet_id = self.game_state.next_fleet_id
        self.game_state.next_fleet_id += 1
        self.game_state.fleets.append(fleet)

    def get_trip_length(self, source_planet: Planet, destination_planet: Planet):
        x_dist = source_planet.x_pos - destination_planet.x_pos
        y_dist = source_planet.y_pos - destination_planet.y_pos
        return int(math.sqrt(x_dist ** 2 + y_dist ** 2))

    def process_command(self, command: FleetCommand, player_id: int):
        source_planet = self.game_state.get_planet(command.source_planet)
        destination_planet = self.game_state.get_planet(command.destination_planet)

        if not source_planet:
            print(f'Player {player_id} tried to launch {ships} ships from unknown planet {command.source_planet}')
            return

        if command.ships <= 0:
            print(f'Player {player_id} tried to launch {command.ships} ships from {source_planet}')
            return

        if command.ships >= source_planet.ships:
            print(f'Player {player_id} tried to launch too may ships {command.ships} from {source_planet} '
                  f'(it has only {source_planet.ships} ships)')
            return

        if not destination_planet:
            print(f'Player {player_id} tried to launch {command.ships} from {source_planet} '
                  f'to an unknown planet {command.destination_planet}')
            return

        if source_planet.player_id != player_id:
            print(
                f'Player {player_id} tried to launch {command.ships} ships '
                f'from planet {source_planet} which it doesn\'t own')
            return

        if source_planet == destination_planet:
            print(f'Player {player_id} tried to send {command.ships} ships to/from {source_planet}')
            return

        self.launch_fleet(source_planet, destination_planet, command.ships)


class GameState:
    def __init__(self):
        self.planets = list()
        self.fleets = list()

        self.current_player = None
        self.enemy_player = None

        self.next_fleet_id = 1

    def get_planet(self, planet_id: int):
        return next((planet for planet in self.planets if planet.planet_id == planet_id), None)

    def get_planets(self):
        return self.planets

    def get_my_planets(self):
        return self.get_player_planets(self.current_player)

    def get_enemy_planets(self):
        return self.get_player_planets(self.enemy_player)

    def get_neutral_planets(self):
        return self.get_player_planets(0)

    def get_player_planets(self, player_id: int):
        if player_id not in [0, 1, 2]:
            raise ValueError('Cannot get planets for players other than 0,1,2')

        return [planet for planet in self.planets if planet.player_id == player_id]

    def get_fleet(self, fleet_id):
        return next((fleet for fleet in self.fleets if fleet.fleet_id == fleet_id), None)

    def get_fleets(self):
        return self.fleets

    def get_my_fleets(self):
        return self.get_player_fleets(self.current_player)

    def get_enemy_fleets(self):
        return self.get_player_fleets(self.enemy_player)

    def get_player_fleets(self, player_id: int):
        if player_id not in [1, 2]:
            raise ValueError('Can only get fleets for players 1 and 2')

        return [fleet for fleet in self.fleets if fleet.player_id == player_id]

    def is_player_alive(self, player_id: int):
        return self.get_player_planets(player_id) or self.get_player_planets(player_id)

    def get_total_ship_count(self, player_id: int):
        planet_ships = sum([planet.ships for planet in self.get_player_planets(player_id)])
        fleet_ships = sum([fleet.ships for fleet in self.get_player_fleets(player_id)])
        return planet_ships + fleet_ships

    def get_winning_player(self):
        player_1_ships = self.get_total_ship_count(1)
        player_2_ships = self.get_total_ship_count(2)

        if player_1_ships > player_2_ships:
            return 1
        elif player_2_ships > player_1_ships:
            return 2
        else:
            return 0

    def get_lost_player(self):
        if self.get_total_ship_count(1) == 0:
            return 1
        elif self.get_total_ship_count(2) == 0:
            return 2
        else:
            return 0

    def get_my_planet_count(self):
        return len(self.get_my_planets())

    def get_enemy_planet_count(self):
        return len(self.get_enemy_planets())
