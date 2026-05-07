## Grid Rivalry
Author: Simran Shergill, Demarcus Simpson-Johnson, Leota Wiswakarma
Course: INST326


ABOUT THE GAME
--------------
Grid Rivalry is a single-player survival game played on a 10x10 grid.
You start in the top-left corner and your goal is to reach the exit [*] in the
bottom-right corner. The grid is full of hidden cells (shown as ?), collectible
tools (shown in green), blocking obstacles (shown in red), and three enemies
that move around on their own every half second.

HOW TO RUN 
-----------
Open Terminal, navigate to the final_project_collab folder/the directory that
the program "final_project_test.py" is in. 
Type in "python3 final_project_test.py" and Enter. 

HOW TO PLAY
-----------
Use the arrow keys to move one cell at a time. Every cell you step on gets
revealed. Tools appear as (k), (l), (w), (r), (p) in green — walk onto them
to automatically pick them up and add them to your bag. Obstacles appear as
[D], [L], [X], [^], [V] in red and are hard walls — you cannot pass through
them at all unless you are already carrying the matching tool. When you walk
into an obstacle while holding the right tool, the obstacle clears and the
tool is consumed from your bag.


Three enemies roam the grid automatically:
 S (Shadow)  — if it lands on you, it steals your last collected tool
 G (Ghost)   — if it lands on you, it sends you straight back to the start
 B (Bomber)  — if it lands on you, it wipes your entire bag clean


Every hit from any enemy also costs you one life and resets you to the start.
You have 3 lives total. Lose all three and it is game over.


Every 8 moves you make, a new random obstacle spawns somewhere on the grid,
so the longer you take, the harder it gets.


TOOL — OBSTACLE PAIRS
----------------------
 (k) key         unlocks  [D] door
 (w) wood plank  crosses  [L] lava
 (r) rock        defeats  [X] dragon
 (l) ladder      scales   [^] cliff up
 (p) parachute   clears   [V] hole down


SCORING
-------
 +10 points for picking up a tool
 +20 points for clearing an obstacle


Controls: arrow keys to move, Q to quit.


