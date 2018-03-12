AutoPylot
=========
**AutoPylot** is a programming game where players compete by writing
bots that give commands to one of two space empires fighting for domination over
a single solar system.

### Rules of the Game

 - A symmetrical solar system is created with each player given control
 of a single planet on either side of the system.
 Every other planet in the system starts out neutral
 - Every planet in the system starts with a number of ships, including
 tne neutral planets
 - Every turn each planet controlled by a player is given more ships.
 The exact rate of ship growth depends on the size of the planet.
 - Fleets of ships can be launched from a planet to attack enemy or
 neutral planets. If the number of ships in the attacking fleet is
 greater than the number of ships on the planet, then the attacking
 player gains control of the planet
 - Fleets can also be send to reinforce friendly planets

### Victory Conditions

Players are tasked with writing a bot that wins the game by
either taking control of every planet that the enemy bot possesses, or
controlling more ships than the opposition by the 500th turn
(ships in fleets and on planets both count towards the secondary win condition)

### Creating a Bot

To create a bot, place a new Python script in the "bots" folder with the name "my_bot.py"
Inside the script, you should use the following imports:
```
from game_state import GameState, FleetCommand
```

At the beginning of every turn, each bot will be given a `GameState`
object, and will be expected to return a number of `FleetCommand` objects.
A `FleetCommand` is a command to send a fleet from one planet to another.
There are some obvious rules regarding a valid `FleetCommand`:
 - Players cannot send ships from planets that they do not control
 - Players cannot send more ships from a planet then are currently on that planet
 - Players cannot send a fleet that has the same source/destination planet

