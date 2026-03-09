import heapq
from solver import Solver

class AStarSolver(Solver):
    def __init__(self, initial_grid: list[list[int]], grid_size: int):
        super().__init__(initial_grid, grid_size)
        
        self.open_list = []
        self.closed_set = set()
        
        # Calculate initial heuristic (number of empty cells)
        h_cost = sum(row.count(0) for row in self.initial_state)
        # Queue stores: (f_cost, -g_cost, state) 
        # Negative g_cost forces the AI to prioritize deeper nodes if f_costs are equal!
        heapq.heappush(self.open_list, (0 + h_cost, 0, self.initial_state))

    def get_next_step(self) -> tuple[tuple, str]:
        if self.is_finished:
            return None, "Already finished!"

        if not self.open_list:
            self.is_finished = True
            return None, "Failed: No solution found."

        # Pop the state with the lowest f_cost (and deepest g_cost tiebreaker)
        f_cost, neg_g_cost, current_state = heapq.heappop(self.open_list)
        g_cost = -neg_g_cost 
        
        self.closed_set.add(current_state)

        # Check if it is the goal state
        h_cost = sum(row.count(0) for row in current_state)
        if h_cost == 0 and self.is_valid_partial_state(current_state):
            self.is_finished = True
            self.is_solved = True
            return current_state, "Solved"

        # Find the FIRST empty cell to expand
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
            for val in (1, 2):
                new_state = list(list(row) for row in current_state)
                new_state[empty_r][empty_c] = val
                new_state = tuple(tuple(row) for row in new_state)

                # The new valid state check happens right here!
                if new_state not in self.closed_set and self.is_valid_partial_state(new_state):
                    new_h = h_cost - 1
                    new_g = g_cost + 1
                    new_f = new_g + new_h
                    heapq.heappush(self.open_list, (new_f, -new_g, new_state))

        return current_state, "Searching..."