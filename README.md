Python 3.12.8

Requirements:
```
pip install pygame
```

How to run:
- Run Hill Climbing algorithm
```
python binairo.py hill_climbing.py
```

- Run DFS algorithm
```
python binairo.py dfs.py
```

How to run benmark:
1. Requirement:
```
pip install pandas openpyxl
```

2. Run:
```
python run_benmarks.py
```

RULE:
1. No Three in a Row: You cannot have more than two of the same number next to each other, either horizontally or vertically. EX:
    - Allowed: 0 0 1 1 0 1, 1 1 0 0 1 0
    - Not Allowed: 1 1 0 0 0 1 or 1 1 1 0 0 0
    
2. Equal Balance: Each row and each column must contain an equal number of 0s and 1s.
    Example: In a 10x10 grid, every row must have exactly five 0s and five 1s.

3. Unique Lines: No two rows can be identical, and no two columns can be identical. (Rows can look like columns, but Row A cannot look exactly like Row B).


CONVENTION:
- Input: list[list[int]]
```
    [[1, 0, 0, 0, 2, 0],
    [0, 0, 2, 2, 0, 1],
    [0, 2, 1, 0, 0, 1],
    [1, 0, 2, 2, 1, 0],
    [0, 0, 0, 0, 0, 2],
    [0, 1, 0, 0, 2, 1]]
```
    * "0" stands for empty cell.
    * "1" and "2" stand for black and white circles.

- Output: the finished state of the input after being solved and use pygame to simulate.



DFS idea: 
- Use stack to store possible states and a visited list to store proccessed states. 
- Each step, pop a state from stack and check whether it is valid state, if valid-> finish, else add 2 new states by finding an empty cell and fill 1 and 2, then repeat until done.
- A level is unsolvable when the stack is empty (no possible states).

- Pseudo code:
```
def init():
    stack = []
    visited = {}
    init_state = input

def get_next_step():
    if stack is empty: -> unsolvable

    new_state = stack.pop()
    if new_state is valid: -> finished

    # Check state is visited?
    while new_state is in visited:
        if stack is empty: -> unsolvable
        new_state = stack.pop()
    
    visited.add(new_state)

    pos_cell_x, pos_cell_y = find_next_empty_cell()

    first_new_state = new_state
    first_new_state[pos_cell_x][pos_cell_y] = 1

    second_new_state = new_state
    second_new_state[pos_cell_x][pos_cell_y] = 2

    stack.add(second_new_state)
    stack.add(first_new_state)
```



Hill Climbing idea:
- Counting conflicts (how many rules are broken) at current state as heuricstic function.
- The goal is to reach exactly 0 conflict.
- Initially, add randomly 1 or 2 val at each cell in the entire grid.
- Each step, loop each cell and create a new state by flip that cell (flip 1 to 2, or 2 to 1), if that new state's conflict < current state one -> update current state.
- Repeat until conflict is 0 or exceeding the limit ( = level is unsolvable).

- Pseudo code:
```
def init():
    max_limit = 0
    cur_limit = 0
    cur_state = fill_random_value(input)

def get_next_step():
    cur_conflict = count_conflict(cur_state)
    if cur_conflict = 0: -> finished

    if cur_limit > max_limit: -> unsolvable

    for r, c in cur_state:
        new_state = cur_state
        new_state[r][c] = flip_cell()
        
        new_conflict = count_conflict(new_state)
        if new_conflict < cur_conflict:
            update_state()

    if can not update state: -> cur_state = fill_random_value(cur_state)

```



BENMARK EXPLAIN:
1. Memory Consumption:
- DFS (Blind Search): Consumes a lot of memory. It must store every board state it visits (using a Stack and a Visited set) so it can backtrack later. The harder the level, the larger the search tree, and the more memory it eats up.

- Hill Climbing (Heuristic Search): Consumes very little memory. It only keeps track of the current board and its immediate neighbors to calculate the heuristic score (number of rule conflicts). It does not remember past moves, keeping memory usage low and constant.

2. Execution Time:
- DFS: Steady but can be slow. It blindly tests combinations. If the correct solution is buried deep in the search tree, DFS wastes a lot of time exploring wrong paths before finding the right one.

- Hill Climbing: Usually very fast, but unpredictable. The heuristic guides it quickly toward the correct answer. However, it can easily get stuck in a "Local Maximum" (a state where no single move improves the board). When stuck, it is forced to do a "Random Restart," which causes the execution time to fluctuate significantly across different runs.

***Summary:
- DFS guarantees a solution but is heavy on memory and time. 
- Hill Climbing is lightweight and fast, but relies on luck (random restarts) to escape dead ends.


