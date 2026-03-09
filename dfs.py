from solver import Solver

class DFSSolver(Solver):
    def __init__(self, initial_grid: list[list[int]], grid_size: int):
        super().__init__(initial_grid, grid_size)
        
        self.stack = [self.initial_state]
        self.visited = set()

    def get_next_step(self) -> tuple[tuple, str]:
        if self.is_finished:
            return None, "Already finished"

        if not self.stack:
            self.is_finished = True
            return None, "No solution found."

        # Pop the most recently added state from the top of the stack
        current_state = self.stack.pop()
        
        # If encountering a state already processed, skip it to save time
        while current_state in self.visited:
            if not self.stack:
                self.is_finished = True
                return None, "No solution found."
            current_state = self.stack.pop()

        self.visited.add(current_state)

        # Check if it is the goal state
        h_cost = sum(row.count(0) for row in current_state)
        if h_cost == 0 and self.is_valid_partial_state(current_state):
            self.is_finished = True
            self.is_solved = True
            return current_state, "Solved"

        # Find the first empty cell to expand
        empty_r, empty_c = -1, -1
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if current_state[r][c] == 0:
                    empty_r, empty_c = r, c
                    break
            if empty_r != -1:
                break

        # Generate children
        if empty_r != -1:
            # push '2' then '1' so that '1' is at the top of the stack and gets evaluated first
            for val in (2, 1):
                new_state = list(list(row) for row in current_state)
                new_state[empty_r][empty_c] = val
                new_state = tuple(tuple(row) for row in new_state)

                if new_state not in self.visited and self.is_valid_partial_state(new_state):
                    self.stack.append(new_state)

        return current_state, "Searching..."