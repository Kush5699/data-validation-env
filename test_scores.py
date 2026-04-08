import sys
sys.path.insert(0, ".")
from env.environment import DataValidationEnvironment
from env.models import DataCleanAction

env = DataValidationEnvironment()

EASY_FIXES = [
    ("fix_missing", "email", 1, "bob@example.com"),
    ("fix_missing", "department", 2, "Engineering"),
    ("fix_missing", "name", 4, "Eve Davis"),
]

MEDIUM_FIXES = [
    ("fix_type", "price", 0, "999.99"),
    ("fix_type", "quantity", 2, "500"),
    ("fix_format", "sku", 3, "MN-004"),
    ("fix_missing", "category", 5, "Audio"),
    ("fix_range", "price", 4, "79.99"),
    ("fix_duplicate", "sku", 6, "WC-007"),
]

HARD_FIXES = [
    ("fix_missing", "email", 0, "orders@acme.com"),
    ("fix_range", "amount", 1, "2300.50"),
    ("fix_format", "date", 2, "2024-03-17"),
    ("fix_type", "amount", 3, "4200.00"),
    ("fix_format", "status", 4, "pending"),
    ("fix_missing", "region", 5, "Europe"),
    ("fix_duplicate", "customer", 6, "PeakTech"),
    ("fix_range", "amount", 7, "6750.00"),
    ("fix_format", "currency", 8, "AUD"),
    ("fix_missing", "priority", 9, "low"),
]

ALL_TASKS = {
    "easy_missing_values": EASY_FIXES,
    "medium_mixed_errors": MEDIUM_FIXES,
    "hard_multi_constraint": HARD_FIXES,
}

print("=" * 60)
print("TESTING ALL VALUES FOR 0.0 OR 1.0")
print("=" * 60)

found_issue = False

for task_name, fixes in ALL_TASKS.items():
    print(f"\n--- {task_name} ---")
    
    # Test 1: Perfect play (fix all errors)
    obs = env.reset(task_name, 42)
    print(f"  RESET: reward={obs.reward}, cumulative={obs.cumulative_reward}, progress={obs.progress_pct}")
    
    if obs.reward == 0.0 or obs.reward == 1.0:
        print(f"  *** FOUND 0.0 or 1.0 in reset reward! ***")
        found_issue = True
    if obs.cumulative_reward == 0.0 or obs.cumulative_reward == 1.0:
        print(f"  *** FOUND 0.0 or 1.0 in reset cumulative! ***")
        found_issue = True
    
    all_rewards = []
    for i, (atype, field, row, val) in enumerate(fixes):
        action = DataCleanAction(action_type=atype, target_field=field, target_row=row, new_value=val)
        obs = env.step(action)
        all_rewards.append(obs.reward)
        print(f"  STEP {i+1}: reward={obs.reward}, cumulative={obs.cumulative_reward}, done={obs.done}, progress={obs.progress_pct}")
        
        if obs.reward == 0.0 or obs.reward == 1.0:
            print(f"  *** FOUND 0.0 or 1.0 in step reward! ***")
            found_issue = True
        if obs.cumulative_reward == 0.0 or obs.cumulative_reward == 1.0:
            print(f"  *** FOUND 0.0 or 1.0 in step cumulative! ***")
            found_issue = True
    
    # Check state
    state = env.state()
    print(f"  STATE: cumulative={state.cumulative_reward}")
    if state.cumulative_reward == 0.0 or state.cumulative_reward == 1.0:
        print(f"  *** FOUND 0.0 or 1.0 in state cumulative! ***")
        found_issue = True
    
    # Check various score computations
    total_reward = sum(all_rewards)
    avg_reward = total_reward / len(all_rewards) if all_rewards else 0
    errors_ratio = obs.errors_fixed / obs.errors_total if obs.errors_total > 0 else 0
    
    print(f"  SCORES: sum={total_reward}, avg={avg_reward}, errors_ratio={errors_ratio}")
    
    if total_reward == 0.0 or total_reward == 1.0:
        print(f"  *** sum is exactly 0.0 or 1.0! ***")
        found_issue = True
    if avg_reward == 0.0 or avg_reward == 1.0:
        print(f"  *** avg is exactly 0.0 or 1.0! ***")
        found_issue = True
    if errors_ratio == 0.0 or errors_ratio == 1.0:
        print(f"  *** errors_ratio is exactly 0.0 or 1.0! ***")
        found_issue = True

    # Test 2: No play (just reset, no steps)
    obs2 = env.reset(task_name, 42)
    no_play_ratio = obs2.errors_fixed / obs2.errors_total if obs2.errors_total > 0 else 0
    print(f"  NO-PLAY: errors_ratio={no_play_ratio}")
    if no_play_ratio == 0.0 or no_play_ratio == 1.0:
        print(f"  *** no-play errors_ratio is exactly 0.0 or 1.0! ***")
        found_issue = True

print(f"\n{'=' * 60}")
if found_issue:
    print("ISSUES FOUND! See *** markers above.")
else:
    print("ALL CLEAR - no 0.0 or 1.0 found anywhere!")
