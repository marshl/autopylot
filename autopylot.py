from multiprocessing import Pool
import os
from os import path
from time import time

from tkinter import *
import tkinter.ttk as ttk

from game_state import *


class SimulationCanvas(Frame):
    def __init__(self, master=None, *args, **kwargs):
        Frame.__init__(self, master)
        self.max_x = self.max_y = 25
        self.canvas_width = 512
        self.canvas_height = self.canvas_width * self.max_x / self.max_y

        self.x_scale_factor = self.canvas_width / self.max_x
        self.y_scale_factor = self.canvas_height / self.max_y

        self.controller = None
        self.simulation_canvas = Canvas(self, background='black', width=self.canvas_width, height=self.canvas_height)
        self.simulation_canvas.pack()

        self.planet_shapes = {}
        self.planet_labels = {}
        self.fleets = {}

    def initialise(self, controller: GameController):
        self.controller = controller
        self.simulation_canvas.delete('all')

        self.planet_shapes = {}
        self.planet_labels = {}

        for planet in controller.game_state.get_planets():
            x_pos, y_pos = self.map_to_canvas_coord(planet.x_pos, planet.y_pos)
            size = (planet.ship_growth + 3) * 3.5
            shape = self.simulation_canvas.create_oval((x_pos, y_pos, x_pos + size, y_pos + size))
            self.planet_shapes[planet.planet_id] = shape

            label = self.simulation_canvas.create_text(x_pos + size / 2, y_pos + size / 2, fill='white',
                                                       anchor='center')
            self.planet_labels[planet.planet_id] = label

    @staticmethod
    def get_player_color(player_id: int):
        return {0: 'blue', 1: 'red', 2: 'green'}[player_id]

    def callback(self):
        pass

    def map_to_canvas_coord(self, x_pos, y_pos):
        return self.x_scale_factor * x_pos, self.y_scale_factor * y_pos

    def get_fleet_position(self, fleet: Fleet):

        source_planet = self.controller.game_state.get_planet(fleet.source_planet)
        destination_planet = self.controller.game_state.get_planet(fleet.destination_planet)

        start_x, start_y = self.map_to_canvas_coord(source_planet.x_pos, source_planet.y_pos)
        end_x, end_y = self.map_to_canvas_coord(destination_planet.x_pos, destination_planet.y_pos)

        travel_delta = fleet.get_turns_travelled() / fleet.total_trip_length

        return start_x + (end_x - start_x) * travel_delta, start_y + (end_y - start_y) * travel_delta

    def update_canvas(self):

        for planet_id, oval_id in self.planet_shapes.items():
            planet = self.controller.game_state.get_planet(planet_id)
            color = self.get_player_color(planet.player_id)
            self.simulation_canvas.itemconfig(oval_id, fill=color)

        for planet_id, label_id in self.planet_labels.items():
            planet = self.controller.game_state.get_planet(planet_id)
            self.simulation_canvas.itemconfig(label_id, text=str(planet.ships))

        # Remove fleets that have landed
        for fleet_id in list(self.fleets.keys()):
            if not self.controller.game_state.get_fleet(fleet_id):
                label_id = self.fleets[fleet_id]
                self.simulation_canvas.delete(label_id)
                del self.fleets[fleet_id]

        # Add fleets that have launched
        for fleet in self.controller.game_state.get_fleets():
            if fleet.fleet_id not in self.fleets:
                label_id = self.simulation_canvas.create_text(0, 0, fill=self.get_player_color(fleet.player_id),
                                                              anchor='center', text=str(fleet.ships))
                self.fleets[fleet.fleet_id] = label_id

        # Update position of all fleets
        for fleet_id, label_id in self.fleets.items():
            fleet = self.controller.game_state.get_fleet(fleet_id)
            x_pos, y_pos = self.get_fleet_position(fleet)
            self.simulation_canvas.coords(label_id, x_pos, y_pos)


class AutopylotFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.map_files = self.get_map_files('maps')
        self.bot_files = self.get_bot_files('bots')
        self.bots = self.load_bots()

        self.controller = GameController()
        self.is_game_running = False

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        maps_frame = ttk.Frame(self.main_frame)
        maps_frame.grid(column=3, row=2)

        bot_name_list = StringVar(value=[bot.name for bot in self.bots])
        self.left_bot_frame, self.left_bot_listbox = self.create_bot_frame(self.main_frame, bot_name_list)
        self.left_bot_frame.grid(column=1, row=2)
        ttk.Label(self.main_frame, text='Player 1', foreground=SimulationCanvas.get_player_color(1)) \
            .grid(column=1, row=1, sticky=S)

        self.right_bot_frame, self.right_bot_listbox = self.create_bot_frame(self.main_frame, bot_name_list)
        self.right_bot_frame.grid(column=2, row=2)
        ttk.Label(self.main_frame, text='Player 2', foreground=SimulationCanvas.get_player_color(2)) \
            .grid(column=2, row=1, sticky=S)

        map_vars = StringVar(value=self.map_files)
        scrollbar = ttk.Scrollbar(maps_frame, orient=VERTICAL)
        self.map_listbox = Listbox(maps_frame, height=10, listvariable=map_vars, exportselection=0,
                                   yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.map_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.map_listbox.pack(side=RIGHT, fill=Y)
        ttk.Label(self.main_frame, text='Maps').grid(column=3, row=1, sticky=S)

        buttons_frame = Frame(self.main_frame)
        buttons_frame.grid(column=1, row=3, columnspan=3)
        self.start_button = ttk.Button(buttons_frame, text='Start', command=self.start_game)
        self.start_button.pack(side=LEFT)

        self.resume_button = ttk.Button(buttons_frame, text='Resume', command=self.resume_game)
        self.resume_button.config(state=DISABLED)
        self.resume_button.pack(side=LEFT)

        self.stop_button = ttk.Button(buttons_frame, text='Stop', command=self.stop_game)
        self.stop_button.config(state=DISABLED)
        self.stop_button.pack(side=LEFT)

        self.autoplay_button = ttk.Button(buttons_frame, text='Play All', command=self.play_all_games)
        self.autoplay_button.pack(side=LEFT)

        self.message_box = Text(self.main_frame)
        self.message_box.config(state=DISABLED)
        self.message_box.grid(column=4, row=1, rowspan=4)

        self.game_frame = SimulationCanvas(self.main_frame)
        self.game_frame.grid(column=1, row=4, columnspan=3)

        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def get_map_files(self, map_path: str):
        return [file for file in os.listdir(map_path) if path.isfile(path.join(map_path, file))]

    def get_bot_files(self, bot_path: str):
        return [file for file in os.listdir(bot_path) if path.isfile(path.join(bot_path, file))]

    def load_bots(self):
        files = [file for file in os.listdir('bots') if path.isfile(path.join('bots', file))]
        bots = [Bot(file) for file in files]
        return bots

    def create_bot_frame(self, parent_frame: Frame, bot_names):
        bot_frame = ttk.Frame(parent_frame)

        scrollbar = ttk.Scrollbar(bot_frame, orient=VERTICAL)
        bots_listbox = Listbox(bot_frame, height=10, listvariable=bot_names, exportselection=0,
                               yscrollcommand=scrollbar.set)

        scrollbar.config(command=bots_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        bots_listbox.pack(side=RIGHT, fill=Y)

        return bot_frame, bots_listbox

    def start_game(self):
        if self.is_game_running:
            return

        bot_1_index = self.left_bot_listbox.curselection()
        bot_2_index = self.right_bot_listbox.curselection()
        map_index = self.map_listbox.curselection()

        if not bot_1_index or not bot_2_index or not map_index:
            return

        bot_1 = self.bots[bot_1_index[0]]
        bot_2 = self.bots[bot_2_index[0]]
        map_name = self.map_files[map_index[0]]

        self.controller.start_game(bot_1, bot_2)

        self.controller.load_map_file('maps/' + map_name)
        self.game_frame.initialise(self.controller)

        self.stop_button.config(state=NORMAL)
        self.start_button.config(state=DISABLED)
        self.resume_button.config(state=DISABLED)
        self.is_game_running = True

        self.update_game()

    def stop_game(self):
        self.stop_button.config(state=DISABLED)
        self.resume_button.config(state=NORMAL)
        self.start_button.config(state=NORMAL)
        self.is_game_running = False

    def resume_game(self):
        if self.is_game_running:
            return

        self.stop_button.config(state=NORMAL)
        self.resume_button.config(state=DISABLED)
        self.start_button.config(state=DISABLED)

        self.is_game_running = True
        self.update_game()

    def update_game(self):

        self.controller.turn_step()
        self.game_frame.update_canvas()

        result = self.controller.get_game_result()
        if result:
            self.add_message(str(result))
            self.stop_game()
            return

        self.after(int(1000 / 12), self.update_game)

    def add_message(self, message: str):
        self.message_box.configure(state=NORMAL)
        self.message_box.insert(END, message + '\n')
        self.message_box.see(END)
        self.message_box.configure(state=DISABLED)

    def play_all_games(self):
        if self.is_game_running:
            return

        pairs = [(x, y) for x_idx, x in enumerate(self.bots) for y_idx, y in enumerate(self.bots) if x_idx < y_idx]
        pair_maps = [(bot_1, bot_2, map_file) for bot_1, bot_2 in pairs for map_file in self.map_files]
        pool = Pool(processes=8)
        results = pool.map(autoplay_map, pair_maps)

        for result in results:
            self.add_message(str(result))

        for bot in self.bots:
            win_count = sum([result.get_winning_bot().name == bot.name for result in results])
            lose_count = sum([result.get_losing_bot().name == bot.name for result in results])
            draw_count = sum([result.winning_player == 0 for result in results])
            self.add_message(f'{bot.name} won {win_count} games and lost {lose_count} games (drew {draw_count} games)')


def autoplay_map(args):
    bot_1 = args[0]
    bot_2 = args[1]
    map_file = args[2]
    controller = GameController()
    controller.start_game(bot_1, bot_2)

    controller.load_map_file('maps/' + map_file)

    while True:
        controller.turn_step()
        result = controller.get_game_result()
        if result:
            return result


if __name__ == '__main__':
    root = Tk()
    root.title = 'Autopylot'
    gui = AutopylotFrame(root)
    gui.pack()
    root.mainloop()
