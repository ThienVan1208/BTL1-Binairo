from abc import ABC, abstractmethod

class Solver(ABC):
    def __init__(self, initial_grid: list[list[int]], grid_size: int):
        self.grid_size = grid_size
        # Convert the starting grid into a tuple of tuples so it is immutable and hashable
        self.initial_state = tuple(tuple(row) for row in initial_grid)
        self.is_finished = False
        self.is_solved = False

    @abstractmethod
    def get_next_step(self) -> tuple[tuple, str]:
        """
        Executes one single step of the algorithm.
        Returns the current evaluated state (2D tuple) and a status message.
        """
        pass
    
    def is_valid_partial_state(self, state: tuple) -> bool:
        """
        Validates the board state against all Binairo rules.
        """
        max_count = self.grid_size // 2

        # Check Rows
        for row in state:
            if row.count(1) > max_count or row.count(2) > max_count:
                return False
            for i in range(self.grid_size - 2):
                if row[i] != 0 and row[i] == row[i+1] == row[i+2]:
                    return False

        # Duplicate Row Check (Only for fully filled rows)
        filled_rows = [row for row in state if 0 not in row]
        if len(filled_rows) != len(set(filled_rows)):
            return False

        # Check Columns
        cols = tuple(tuple(state[r][c] for r in range(self.grid_size)) for c in range(self.grid_size))
        for col in cols:
            if col.count(1) > max_count or col.count(2) > max_count:
                return False
            for i in range(self.grid_size - 2):
                if col[i] != 0 and col[i] == col[i+1] == col[i+2]:
                    return False

        # 4. Duplicate Column Check (Only for fully filled columns)
        filled_cols = [col for col in cols if 0 not in col]
        if len(filled_cols) != len(set(filled_cols)):
            return False

        return True