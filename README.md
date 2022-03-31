# Snak
Snak is an esolang based on the classic snake game.

## Installation
You will need python3. To use the visualizer, you will need the curses module. Then it's as easy as:
```
python3 snak.py [-q] filename length
```

## Snak program definition

### Grid chunks
A Snak program consists of a description of a single chunk in an infinite 2D space.
The contents of each cell of the space are defined by the character located in that position in the program. These include

| Symbol | Meaning                      |
| :----: | -------                      |
| \+     | Incrementing Fruit           |
| \-     | Decrementing Fruit           |
| \>     | Snake initially moving east  |
| \<     | Snake initially moving west  |
| ^      | Snake initially moving north |
| v      | Snake initially moving south |

All other characters (aside from line feeds and carriage returns, which are stripped) have no semantic meaning (but do occupy space). (Thus, Snak programs can contain comments in their unused space. It is recommended to replace the letter v, where needed in such comments, with a u or w.)

The full operating space of a Snak program is created by infinitely tiling the fruits in the single defined chunk in every direction.

The width of the chunks is defined as the maximum length of any line of the program. The height of the chunks is defined as the number of lines in the program.

### Snakes
A Snak program may have any number of snakes. A snake has a position, a direction, a length, and a finite queue of cells in the grid (the last of which is always its position). At program start, every snake occupies only a single cell in the prescribed location in the origin chunk (the chunk that contains the location (0,0)), regardless of its initial length.

### Fruits
Every + or - in the program definition specifies an infinite number of corresponding fruits, one per chunk. As the program runs, some fruits will be removed from the grid, but, unlike the snake game, no fruits are ever added.

## Execution of a Snak program
At the beginning of a Snak program, the length of every snake is initialized to the same value provided as the length parameter to the interpreter. This is the only input method that does not involve altering the program source.

A Snak program proceeds in finite ticks. At each tick, the following occur in sequence:
1. Every snake takes one step in its current direction. 
   1. The new position is enqueued in its list of occupied cells. 
   2. The oldest position in the queue is popped and discarded.
   3. If the snake's position is now a cell it already occupies, the program halts.
2. If any snake now occupies a cell occupied by any other snake, the program halts.
3. If any snake now occupies the same position as a fruit:
   1. That fruit is removed from the grid.
   2. The corresponding incrementing or decrementing of the snake's length is performed.
      - If a decrementing brings a snake's length to zero, the program halts with an error condition.
   3. If a snake now occupies more cells than its length, its queue of occupied positions is popped.
4. Every snake's direction is updated.
   1. Up to three fruits are selected from the grid.
      - A fruit is selected if it is the first fruit along the line in the snake's current direction from the snake's current position, or 90 degrees clockwise or counterclockwise from that direction and no snakes (including the snake for whom this computation is being performed) lying between the fruit and the snake's current position. In other words, the first fruit "visible" by the snake in any of the three directions it could take its next step.
   2. Of these selected fruits, the nearest ones to the snake's current position is selected.
   3. If more than one fruit are at the nearest distance, the clockwise one is preferred to the one in the same direction which itself is preferred to the counterclockwise one.

Note that this order ensures that every snake will attempt to take one step in their initially defined direction before the positions of any fruits have an effect on their movement.

When the program halts, the final length of each snake is printed. This is the only form of output aside from watching the program state as it changes.

## Using the interpreter
There is an optional -q flag that turns off the curses-based visualizer/debugger. Using it will cause the program to run to completion (if it halts) as quickly as possible, producing its final result (if any).

Without this flag, you will be dropped into a visualization of the executing program, paused in its initial state, with a number of interaction options available:

| Keyboard Input | What it Does                              |
| :------------: | ------------                              |
| Cursor keys    | Shift the view in the indicated direction |
| p              | Pause/unpause automatic execution         |
| s              | Perform one tick while paused.            |
| \+             | Increase the running speed                |
| \-             | Decrease the running speed                |
| f              | Center view on first defined snake        |
| n              | If centered on snake, select next snake   |
| q              | Halt immediately and exit                 |

If the terminal supports mouse input:

| Mouse Input                 | What it Does                             |
| :---------:                 | ------------                             |
| Right-click on a snake      | Center the head of the snake in the view |
| Right-click on a non-snake  | Stop centering any snakes in the view    |
| Click, hold, and drag       | Drag view                                |

Note that, for weird curses reasons, to drag, you must click and hold still for a moment before beginning to drag. Also, you may need to click on the app for the simulation to keep running after certain interactions (I think this is depends on which term you use.) But

You can resize your terminal at any time to see more or less of the grid.

## See Also

[Esolangs wiki page](<https://esolangs.org/wiki/Snak>)
