Python 3.12.8

Requirements:
```
pip install pygame
```

How to run:
- Run A* algorithm
```
python binairo.py a_star.py
```

- Run DFS algorithm
```
python binairo.py dfs.py
```

RULE:
1. No Three in a Row: You cannot have more than two of the same number next to each other, either horizontally or vertically. EX:
    - Allowed: 0 0 1, 1 0 1
    - Not Allowed: 0 0 0 or 1 1 1
    
2. Equal Balance: Each row and each column must contain an equal number of 0s and 1s.
    Example: In a 10x10 grid, every row must have exactly five 0s and five 1s.

3. Unique Lines: No two rows can be identical, and no two columns can be identical. (Rows can look like columns, but Row A cannot look exactly like Row B).


CONVENTION:
- Input:
    [1, 0, 0, 0, 2, 0],
    [0, 0, 2, 2, 0, 1],
    [0, 2, 1, 0, 0, 1],
    [1, 0, 2, 2, 1, 0],
    [0, 0, 0, 0, 0, 2],
    [0, 1, 0, 0, 2, 1]

    * "0" stands for empty cell.
    * "1" and "2" stand for white and black circles.

- Output: the finished state of the input after being solved and use pygame to simulate.


