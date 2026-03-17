import time
import tracemalloc
import copy
import json
import sys
import os
import pandas as pd

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from dfs import DFSSolver
from hill_climbing import HillClimbingSolver

GRID_SIZE = 6

try:
    with open('levels.json', 'r') as file:
        data = json.load(file)
        LEVELS = data['levels']
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'levels.json'.")
    LEVELS = []

def run_single_benchmark(solver_class, grid):
    """Hàm chạy thuật toán 1 lần và trả về các chỉ số cơ bản"""
    solver = solver_class(copy.deepcopy(grid), GRID_SIZE)
    steps = 0
    
    tracemalloc.start()
    start_time = time.perf_counter()
    
    while not solver.is_finished:
        _, _ = solver.get_next_step()
        steps += 1
        
    elapsed_time = (time.perf_counter() - start_time) * 1000
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_memory_kb = peak_memory / 1024
    is_solved = getattr(solver, 'is_solved', False)
    
    return elapsed_time, peak_memory_kb, steps, is_solved

def main():
    dfs_results = []
    hc_results = []
    
    
    for i, grid in enumerate(LEVELS):
        level_name = f"Level {i + 1}"
        print(f"Proccessing {level_name}...")
        
        # ==========================================
        # 1. ĐÁNH GIÁ DFS (Chỉ cần chạy 1 lần)
        # ==========================================
        dfs_time, dfs_mem, dfs_steps, dfs_solved = run_single_benchmark(DFSSolver, grid)
        dfs_results.append({
            "Level": level_name,
            "Time (ms)": round(dfs_time, 2),
            "Memory (KB)": round(dfs_mem, 2),
            "Steps": dfs_steps,
        })
        
        # ==========================================
        # 2. ĐÁNH GIÁ HILL CLIMBING (Chạy 10 lần lấy trung bình)
        # ==========================================
        RUNS = 10
        total_time = 0
        total_mem = 0
        total_steps = 0
        
        for _ in range(RUNS):
            hc_time, hc_mem, hc_steps, _ = run_single_benchmark(HillClimbingSolver, grid)
            total_time += hc_time
            total_mem += hc_mem
            total_steps += hc_steps
                
        hc_results.append({
            "Level": level_name,
            "Avg Time (ms)": round(total_time / RUNS, 2),
            "Avg Memory (KB)": round(total_mem / RUNS, 2),
            "Avg Steps": round(total_steps / RUNS, 1)
        })

    excel_filename = "result.xlsx"
    
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Table 1: DFS
        df_dfs = pd.DataFrame(dfs_results)
        df_dfs.to_excel(writer, sheet_name='DFS_Results', index=False)
        
        # Table 2: Hill Climbing
        df_hc = pd.DataFrame(hc_results)
        df_hc.to_excel(writer, sheet_name='HillClimbing_Results', index=False)
            
    print(f"\nFinished. Saved in {excel_filename}")

if __name__ == "__main__":
    main()