import random
from solver import Solver

class HillClimbingSolver(Solver):
    def __init__(self, initial_grid: list[list[int]], grid_size: int):
        super().__init__(initial_grid, grid_size)

        self.max_limit = 100
        self.cur_limit = 0
        
        # Keep track of which cells we are allowed to change (the original)
        self.mutable_cells = []
        
        # Create a mutable copy of the initial state
        mutable_state = [list(row) for row in self.initial_state]
        
        # Random Start: Fill all empty cells randomly
        for r in range(grid_size):
            for c in range(grid_size):
                if mutable_state[r][c] == 0:
                    self.mutable_cells.append((r, c))
                    mutable_state[r][c] = random.choice([1, 2])
        
        self.current_state = tuple(tuple(row) for row in mutable_state)

    def count_conflicts(self, state: tuple) -> int:
        """
        The Heuristic: Calculates how many Binairo rules are currently broken.
        Our goal is to reach exactly 0 conflicts.
        """
        conflicts = 0
        n = self.grid_size
        max_c = n // 2

        # Check Rows
        for row in state:
            # Add penalty for unbalanced 1s and 2s
            conflicts += abs(row.count(1) - max_c)
            # Add penalty for 3 or more consecutive identical numbers
            for i in range(n - 2):
                if row[i] == row[i+1] == row[i+2]:
                    conflicts += 1
        
        # Duplicate Rows penalty
        conflicts += (n - len(set(state)))

        # Check Columns
        cols = tuple(tuple(state[r][c] for r in range(n)) for c in range(n))
        for col in cols:
            conflicts += abs(col.count(1) - max_c)
            for i in range(n - 2):
                if col[i] == col[i+1] == col[i+2]:
                    conflicts += 1
        
        # Duplicate Columns penalty
        conflicts += (n - len(set(cols)))

        return conflicts

    def get_next_step(self) -> tuple[tuple, str]:
        if self.is_finished:
            return self.current_state, "Already finished!"

        current_conflicts = self.count_conflicts(self.current_state)

        # Goal Test: Are zero rules broken?
        if current_conflicts == 0:
            self.is_finished = True
            self.is_solved = True
            return self.current_state, "Solved!"
        
        if(self.cur_limit > self.max_limit):
            self.is_finished = True
            self.is_solved = False
            return self.current_state, "No solution found!"

        best_neighbor = None
        best_conflicts = current_conflicts

        # The Climb: Generate all possible neighbors by flipping exactly 1 cell
        for r, c in self.mutable_cells:
            new_state = [list(row) for row in self.current_state]
            
            # Flip 1 to 2, or 2 to 1
            new_state[r][c] = 2 if new_state[r][c] == 1 else 1
            new_state_tuple = tuple(tuple(row) for row in new_state)
            
            neighbor_conflicts = self.count_conflicts(new_state_tuple)
            
            # If this flip results in fewer broken rules, mark it as our best option!
            if neighbor_conflicts < best_conflicts:
                best_conflicts = neighbor_conflicts
                best_neighbor = new_state_tuple

        # --- The "Local Maximum" Problem ---
        # What if NO single flip improves the board? The AI is stuck in a valley!
        if best_neighbor is None:
            # We fix this by doing a "Random Restart" - scramble the board and try again!
            new_state = [list(row) for row in self.initial_state]
            for r, c in self.mutable_cells:
                new_state[r][c] = random.choice([1, 2])
            self.current_state = tuple(tuple(row) for row in new_state)

            self. cur_limit += 1
            
            return self.current_state, f"Stuck in Local Maximum! Random Restarting... (Conflicts: {current_conflicts})"

        # Move to the best neighbor we found
        self.current_state = best_neighbor
        return self.current_state, f"Climbing... (Rules Broken: {best_conflicts})"