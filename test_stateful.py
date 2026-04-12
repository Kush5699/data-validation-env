"""
Comprehensive test: reset + multi-step workflow against local server.
Verifies rewards are strictly in (0, 1) at every point.
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
base = "http://127.0.0.1:8000"
all_ok = True

for task in ["easy_missing_values", "medium_mixed_errors", "hard_multi_constraint"]:
    print(f"\n{'='*60}")
    print(f"TASK: {task}")
    print(f"{'='*60}")

    # Reset
    r = requests.post(f"{base}/reset", json={"task_name": task, "seed": 42})
    d = r.json()
    reset_reward = d["reward"]
    reset_done = d["done"]
    obs = d["observation"]
    errors = obs.get("errors_found", [])
    total_errors = obs.get("errors_total", 0)
    
    print(f"  Reset: reward={reset_reward} done={reset_done} errors={total_errors}")
    
    if reset_reward is None or reset_reward <= 0 or reset_reward >= 1:
        print(f"  ** PROBLEM: reset reward {reset_reward} is out of (0,1) range!")
        all_ok = False

    # Step through errors - try to fix each one
    step_num = 0
    for err in errors:
        step_num += 1
        error_type = err.get("error_type", "")
        field = err.get("field", "")
        row = err.get("row", 0)
        
        # Map error type to action type
        action_map = {
            "missing": "fix_missing",
            "type": "fix_type", 
            "range": "fix_range",
            "format": "fix_format",
            "duplicate": "fix_duplicate",
        }
        action_type = action_map.get(error_type, "skip")
        
        # We'll just send a skip action to test the flow
        action = {
            "action_type": "skip",
            "target_field": field,
            "target_row": row,
            "new_value": "",
        }
        
        r2 = requests.post(f"{base}/step", json={"action": action})
        d2 = r2.json()
        step_reward = d2["reward"]
        step_done = d2["done"]
        
        print(f"  Step {step_num}: reward={step_reward} done={step_done}")
        
        if step_reward is None or step_reward <= 0 or step_reward >= 1:
            print(f"  ** PROBLEM: step reward {step_reward} is out of (0,1) range!")
            all_ok = False
        
        if step_done:
            break
    
    # Try validate action
    r3 = requests.post(f"{base}/step", json={"action": {
        "action_type": "validate",
        "target_field": "",
        "target_row": 0,
        "new_value": "",
    }})
    d3 = r3.json()
    val_reward = d3["reward"]
    val_done = d3["done"]
    print(f"  Validate: reward={val_reward} done={val_done}")
    
    if val_reward is None or val_reward <= 0 or val_reward >= 1:
        print(f"  ** PROBLEM: validate reward {val_reward} is out of (0,1) range!")
        all_ok = False

print(f"\n{'='*60}")
if all_ok:
    print("ALL REWARDS ARE STRICTLY IN (0, 1) - PASS!")
else:
    print("SOME REWARDS FAILED - SEE ABOVE!")
print(f"{'='*60}")
