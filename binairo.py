import pygame
import time
from abc import ABC, abstractmethod
import sys  
from a_star import AStarSolver
from dfs import DFSSolver

# --- Setup & Constants ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Binairo")
clock = pygame.time.Clock()

CELL_COLORS = [(0, 0, 0, 0), (0, 0, 0, 255), (255, 255, 255, 255)]
BG_COLOR = (255, 222, 173, 255)
GRID_LINE_COLOR = (255, 0, 0, 255)
GRID_SIZE = 6
BLOCK_SIZE = 50
FONT_SIZE = 24
FONT = pygame.font.SysFont('Arial', FONT_SIZE)


# --- Base Classes ---
class Cell:
    def __init__(self, val: int = 0):
        self.val = val
        # Lock cell if it has an initial value
        self.is_locked = (val != 0)

    def toggle_value(self):
        """Cycle through 0 -> 1 -> 2 -> 0"""
        if not self.is_locked:
            self.val = (self.val + 1) % 3

    def draw(self, x: int, y: int):
        if self.val in (1, 2):
            pygame.draw.rect(screen, CELL_COLORS[self.val], (x, y, BLOCK_SIZE, BLOCK_SIZE))


class UIElement(ABC):
    def __init__(self):
        self.is_active = True

    @abstractmethod
    def draw(self):
        pass
    
    def handle_event(self, event) -> bool:
        """Returns True if the event was consumed by this UI element."""
        return False


# --- UI Components ---
class TextLabel(UIElement):
    def __init__(self, text='text', color=(255, 255, 255, 255), x=0, y=0, width=1, height=1):
        super().__init__()
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        if not self.is_active:
            return
        text_surface = FONT.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)


class Button(UIElement):
    def __init__(self, text='text', color=(255, 255, 255, 255), x=0, y=0, width=1, height=1, action=None):
        super().__init__()
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.text_label = TextLabel(text, (0, 0, 0, 255), x=self.x, y=self.y, width=self.width, height=self.height)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check for collision
            if (self.x <= mouse_x <= self.x + self.width and 
                self.y <= mouse_y <= self.y + self.height):
                
                if self.action:
                    self.action()
                return True  # Event consumed
        return False

    def draw(self):
        if not self.is_active:
            return
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        self.text_label.draw()


class PopupWindow(UIElement):
    def __init__(self, width=400, height=200):
        super().__init__()
        self.width = width
        self.height = height
        self.x = (SCREEN_WIDTH - width) // 2
        self.y = (SCREEN_HEIGHT - height) // 2

        self.is_visible = False
        self.message = ""
        self.bg_color = (200, 200, 200)

        # OK Button configuration
        btn_w, btn_h = 100, 50
        btn_x = self.x + (self.width - btn_w) // 2
        btn_y = self.y + self.height - btn_h - 20
        self.ok_button = Button("OK", (100, 100, 100), btn_x, btn_y, btn_w, btn_h, action=self.hide)
        
        self.msg_font = pygame.font.SysFont('Arial', 32, bold=True)

    def show(self, message: str, is_win: bool):
        self.message = message
        self.is_visible = True
        self.bg_color = (150, 255, 150) if is_win else (255, 150, 150)

    def hide(self):
        self.is_visible = False

    def handle_event(self, event) -> bool:
        if self.is_visible:
            self.ok_button.handle_event(event)
            return True  # Block other events when popup is open
        return False

    def draw(self):
        if not self.is_visible:
            return
            
        # Draw Shadow
        pygame.draw.rect(screen, (50, 50, 50), (self.x + 5, self.y + 5, self.width, self.height))
        # Draw Background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        # Draw Border
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 3)

        # Draw Message
        text_surf = self.msg_font.render(self.message, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2 - 20))
        screen.blit(text_surf, text_rect)
        
        # Draw Button
        self.ok_button.draw()


# --- Managers ---
class UIManager:
    def __init__(self):
        self.ui_elements: list[UIElement] = []
        self.popup: PopupWindow = None 

    def add_element(self, ui: UIElement):
        self.ui_elements.append(ui)

    def set_popup(self, popup: PopupWindow):
        self.popup = popup

    def handle_event(self, event) -> bool:
        # Priority 1: Popup
        if self.popup and self.popup.handle_event(event):
            return True

        # Priority 2: Standard UI
        for ui in self.ui_elements:
            if ui.handle_event(event):
                return True
        return False

    def draw(self):
        for ui in self.ui_elements:
            ui.draw()
        if self.popup:
            self.popup.draw()


class GridManager:
    def __init__(self, initial_grid: list[list[int]]):
        self.rows = GRID_SIZE
        self.cols = GRID_SIZE
        
        # Convert raw grid to Cell objects
        self.cells = [[Cell(col) for col in row_data] for row_data in initial_grid]

        row_pixels = self.rows * BLOCK_SIZE
        col_pixels = self.cols * BLOCK_SIZE
        self.start_x = (SCREEN_WIDTH - row_pixels) // 2
        self.start_y = (SCREEN_HEIGHT - col_pixels) // 2

    def handle_click(self, pos: tuple[int, int]) -> bool:
        # X position on screen maps to the Column index
        col_idx = (pos[0] - self.start_x) // BLOCK_SIZE
        # Y position on screen maps to the Row index
        row_idx = (pos[1] - self.start_y) // BLOCK_SIZE
        
        if 0 <= row_idx < self.rows and 0 <= col_idx < self.cols:
            self.cells[row_idx][col_idx].toggle_value()
            return True
        return False

    def draw(self):
        for r in range(self.rows):
            for c in range(self.cols):
                # Columns control the horizontal (X) axis
                pixel_x = self.start_x + BLOCK_SIZE * c
                # Rows control the vertical (Y) axis
                pixel_y = self.start_y + BLOCK_SIZE * r
                
                self.cells[r][c].draw(pixel_x, pixel_y)
                pygame.draw.rect(screen, GRID_LINE_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE), 1)

    def validate_grid(self) -> tuple[bool, str]:
        def check_line(line_cells: list[Cell]) -> bool:
            count_1, count_2 = 0, 0
            consecutive, prev_val = 1, -1
            
            for cell in line_cells:
                if cell.val == 0: 
                    return False  # Empty cell found
                
                if cell.val == 1:
                    count_1 += 1
                elif cell.val == 2:
                    count_2 += 1

                if cell.val == prev_val:
                    consecutive += 1
                    if consecutive > 2: 
                        return False # More than 2 consecutive
                else:
                    consecutive = 1
                    prev_val = cell.val
            
            return (count_1 == GRID_SIZE // 2) and (count_2 == GRID_SIZE // 2)

        # Check Lines (Rows & Cols)
        for i in range(GRID_SIZE):
            row = [self.cells[i][c] for c in range(GRID_SIZE)]
            if not check_line(row): 
                return False, f"Row {i} incomplete or invalid!"

            col = [self.cells[r][i] for r in range(GRID_SIZE)]
            if not check_line(col): 
                return False, f"Col {i} incomplete or invalid!"

        # Check Duplicates
        for i in range(GRID_SIZE):
            row_i_vals = [self.cells[i][c].val for c in range(GRID_SIZE)]
            col_i_vals = [self.cells[r][i].val for r in range(GRID_SIZE)]
            
            for j in range(i + 1, GRID_SIZE):
                row_j_vals = [self.cells[j][c].val for c in range(GRID_SIZE)]
                col_j_vals = [self.cells[r][j].val for r in range(GRID_SIZE)]
                
                if row_i_vals == row_j_vals: 
                    return False, f"Duplicate Rows found: {i} & {j}!"
                if col_i_vals == col_j_vals: 
                    return False, f"Duplicate Cols found: {i} & {j}!"

        return True, "YOU WIN!"

class LevelManager:
    def __init__(self, level_list: list[list[list[int]]] = None):
        self.cur_level = 0
        self.__level_list: list[list[list[int]]] = level_list

    def add_level(self, level: list[list[int]]):
        self.__level_list.append(level)

    def add_level_list(self, levels: list[list[list[int]]]):
        self.__level_list.extend(levels)

    def get_level(self, index: int) -> list[list[int]]:
        if index >= len(self.__level_list):
            print('level index is not valid.')
            return None
        
        return self.__level_list[index]
    
    def get_next_level(self) -> list[list[int]]:
        self.cur_level = (self.cur_level + 1) % len(self.__level_list)
        return self.get_level(self.cur_level)

        
class GameManager:
    def __init__(self, solver_type="simple_solver"):
        initial_level =  [
            # Level 1
            [
                [1, 0, 0, 0, 2, 0],
                [0, 0, 2, 2, 0, 1],
                [0, 2, 1, 0, 0, 1],
                [1, 0, 2, 2, 1, 0],
                [0, 0, 0, 0, 0, 2],
                [0, 1, 0, 0, 2, 1]
            ],

            # Level 2
            [
                [1, 0, 2, 1, 0, 0],
                [2, 1, 0, 0, 2, 1],
                [0, 2, 0, 2, 0, 1],
                [0, 2, 1, 0, 1, 0],
                [2, 0, 0, 1, 0, 2],
                [0, 0, 1, 0, 2, 0]
            ],

            # Level 3
            [
                [0, 0, 2, 2, 0, 1],
                [0, 2, 0, 1, 0, 0],
                [1, 0, 2, 2, 0, 2],
                [0, 2, 0, 0, 0, 1],
                [2, 0, 0, 0, 2, 0],
                [1, 0, 0, 1, 0, 0]
            ],

            # Level 4
            [
                [2, 0, 0, 2, 2, 0],
                [0, 2, 0, 0, 0, 2],
                [1, 0, 0, 0, 2, 0],
                [0, 1, 2, 0, 2, 1],
                [0, 0, 1, 2, 0, 0],
                [1, 2, 0, 0, 0, 0]
            ],

            # Level 5
            [
                [1, 0, 2, 1, 0, 2],
                [0, 0, 0, 1, 0, 0],
                [2, 1, 0, 0, 1, 0],
                [0, 0, 0, 2, 1, 2],
                [0, 2, 2, 0, 0, 0],
                [2, 0, 0, 0, 0, 0]
            ],

            # Level 6
            [
                [1, 0, 0, 0, 0, 2],
                [0, 1, 0, 0, 2, 1],
                [2, 0, 2, 2, 0, 0],
                [1, 2, 0, 1, 0, 0],
                [0, 1, 0, 2, 0, 0],
                [0, 0, 1, 1, 0, 1]
            ],

            # Level 7
            [
                [1, 0, 2, 0, 0, 0],
                [0, 0, 1, 2, 0, 2],
                [0, 1, 0, 0, 0, 1],
                [1, 2, 2, 0, 0, 0],
                [0, 0, 0, 2, 1, 0],
                [0, 1, 0, 0, 2, 0]
            ],

            # Level 8
            [
                [0, 0, 1, 2, 0, 1],
                [1, 0, 2, 0, 1, 0],
                [0, 2, 0, 0, 2, 0],
                [0, 0, 0, 0, 0, 1],
                [2, 0, 1, 1, 0, 0],
                [0, 1, 2, 0, 0, 2]
            ],

            # Level 9
            [
                [2, 0, 0, 2, 0, 0],
                [0, 2, 2, 0, 2, 0],
                [0, 0, 0, 2, 1, 0],
                [2, 0, 0, 0, 1, 0],
                [0, 0, 2, 0, 0, 1],
                [0, 2, 0, 1, 0, 2]
            ],

            # Level 10
            [
                [2, 0, 1, 0, 2, 0],
                [0, 2, 0, 1, 0, 1],
                [1, 0, 0, 0, 1, 2],
                [2, 0, 1, 2, 0, 0],
                [0, 1, 0, 1, 0, 0],
                [0, 2, 2, 0, 0, 0]
            ]
        ]
        self.level_manager = LevelManager(initial_level)
        grid = self.level_manager.get_level(0)
        
        self.grid_manager = GridManager(grid)
        self.ai_solver = solver_type

        # Setup UI
        self.ui_manager = UIManager()
        
        check_button = Button('Check', (255, 255, 255), x=10, y=10, width=80, height=40, action=self.check_game)
        step_button = Button('Next Step', (200, 255, 200), x=100, y=10, width=100, height=40, action=self.step_ai)
        solve_button = Button('Fast Solve', (200, 200, 255), x=210, y=10, width=100, height=40, action=self.solve_ai)
        next_level_button = Button('Next level', (200, 200, 255), x=320, y=10, width=100, height=40, action=self.get_next_level)

        self.ui_manager.add_element(check_button)
        self.ui_manager.add_element(step_button)
        self.ui_manager.add_element(solve_button)
        self.ui_manager.add_element(next_level_button)

        self.popup = PopupWindow()
        self.ui_manager.set_popup(self.popup)

        if solver_type == "dfs":
            self.ai_solver = DFSSolver(grid, GRID_SIZE)
            print("--- Initialized DFS Solver ---")
        else:
            self.ai_solver = AStarSolver(grid, GRID_SIZE)
            print("--- Initialized A* Solver ---")


    def get_next_level(self):
        grid = self.level_manager.get_next_level()
        if grid is None: print('next level is none')

        else: self.grid_manager = GridManager(grid)

        if isinstance(self.ai_solver, DFSSolver):
            self.ai_solver = DFSSolver(grid, GRID_SIZE)
            print("--- Initialized DFS Solver ---")
        else:
            self.ai_solver = AStarSolver(grid, GRID_SIZE)
            print("--- Initialized A* Solver ---")
        


    def handle_event(self, event):
        # UI Handles event first
        if self.ui_manager.handle_event(event):
            return

        # Grid handles event if UI didn't take it
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.grid_manager.handle_click(pygame.mouse.get_pos())

    def draw(self):
        self.grid_manager.draw()
        self.ui_manager.draw()

    def check_game(self):
        is_win, message = self.grid_manager.validate_grid()
        self.popup.show(message, is_win)

    def update_grid_from_state(self, state):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid_manager.cells[r][c].val = state[r][c]

    def step_ai(self):
        if self.ai_solver.is_finished:
            return
            
        # methods return (state, status)
        current_state, status = self.ai_solver.get_next_step()
        if current_state:
            self.update_grid_from_state(current_state)
        else:
            print(status)

    def solve_ai(self):
        if self.ai_solver.is_finished:
            return

        start_time = time.perf_counter()
        final_state = None
        status = ''

        while not self.ai_solver.is_finished:
            final_state, status = self.ai_solver.get_next_step()

        elapsed_time = (time.perf_counter() - start_time) * 1000
        print(f"Time taken: {elapsed_time:.2f} ms")

        if final_state:
            self.update_grid_from_state(final_state)
        else:
            print(status)


# --- Main Loop ---
if __name__ == "__main__":
    solver_choice = "simple_solver" 

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if "dfs" in arg:
            solver_choice = "dfs"
        elif "a_star" in arg:
            solver_choice = "a_star"

    game_manager = GameManager(solver_choice)

    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            game_manager.handle_event(event)

        screen.fill(BG_COLOR)
        game_manager.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()





