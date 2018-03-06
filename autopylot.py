import importlib
import os
from os import path

from tkinter import *
import tkinter.ttk as ttk

from game_state import *


def get_map_files(map_path: str):
    return [file for file in os.listdir(map_path) if path.isfile(path.join(map_path, file))]


def get_bot_files(bot_path: str):
    return [file for file in os.listdir(bot_path) if path.isfile(path.join(bot_path, file))]


def create_bot_frame(root_frame, bot_names):
    bot_frame = ttk.Frame(root_frame)

    scrollbar = ttk.Scrollbar(bot_frame, orient=VERTICAL)
    bots_left_listbox = Listbox(bot_frame, height=10, listvariable=bot_names, exportselection=0,
                                yscrollcommand=scrollbar.set)

    scrollbar.config(command=bots_left_listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    bots_left_listbox.pack(side=RIGHT, fill=Y)

    return bot_frame


class SimulationFrame(Frame):
    def __init__(self, master=None, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
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

    def get_player_color(self, player_id: int):
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

        self.controller.turn_step()

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
                label_id = self.simulation_canvas.create_text(0, 0, fill='white', anchor='center',
                                                              text=str(fleet.ships))
                self.fleets[fleet.fleet_id] = label_id

        # Update position of all fleets
        for fleet_id, label_id in self.fleets.items():
            fleet = self.controller.game_state.get_fleet(fleet_id)
            x_pos, y_pos = self.get_fleet_position(fleet)
            self.simulation_canvas.coords(label_id, x_pos, y_pos)

        self.after(int(1000 / 12), self.update_canvas)


if __name__ == '__main__':
    module = importlib.import_module('bots.bot1')

    controller = GameController(module, module)
    controller.load_map_file('maps/map99.txt')

    controller.turn_step()

    root = Tk()
    root.title("autopylot")

    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    maps_frame = ttk.Frame(mainframe)
    maps_frame.grid(column=3, row=2)

    bot_names = StringVar(value=get_bot_files('bots'))
    left_bot_frame = create_bot_frame(mainframe, bot_names)
    left_bot_frame.grid(column=1, row=2)
    ttk.Label(mainframe, text='Player 1').grid(column=1, row=1, sticky=S)

    right_bot_frame = create_bot_frame(mainframe, bot_names)
    right_bot_frame.grid(column=2, row=2)
    ttk.Label(mainframe, text='Player 2').grid(column=2, row=1, sticky=S)

    map_names = StringVar(value=get_map_files('maps'))
    scrollbar = ttk.Scrollbar(maps_frame, orient=VERTICAL)
    maps_listbox = Listbox(maps_frame, height=10, listvariable=map_names, exportselection=0,
                           yscrollcommand=scrollbar.set)
    scrollbar.config(command=maps_listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    maps_listbox.pack(side=RIGHT, fill=Y)
    ttk.Label(mainframe, text='Maps').grid(column=3, row=1, sticky=S)

    ttk.Button(mainframe, text='Go!', command=None).grid(column=3, row=3)

    game_frame = SimulationFrame(mainframe)
    game_frame.grid(column=1, row=4, columnspan=3)
    game_frame.initialise(controller)
    game_frame.update_canvas()

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
