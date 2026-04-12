import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
base = 'https://kush5699-data-validation-env.hf.space'

for task in ['easy_missing_values', 'medium_mixed_errors', 'hard_multi_constraint']:
    print(f'=== TASK: {task} ===')
    
    # Reset
    r = requests.post(f'{base}/reset', json={'task_name': task, 'seed': 42})
    d = r.json()
    reward = d.get('reward')
    done = d.get('done')
    print(f'  Reset: reward={reward}, done={done}, type_reward={type(reward).__name__}')
    
    # Step with skip
    r2 = requests.post(f'{base}/step', json={'action': {'action_type': 'skip', 'target_field': '', 'target_row': 0, 'new_value': ''}})
    d2 = r2.json()
    reward2 = d2.get('reward')
    done2 = d2.get('done')
    print(f'  Step(skip): reward={reward2}, done={done2}, type_reward={type(reward2).__name__}')
    
    # Step with validate
    r3 = requests.post(f'{base}/step', json={'action': {'action_type': 'validate', 'target_field': '', 'target_row': 0, 'new_value': ''}})
    d3 = r3.json()
    reward3 = d3.get('reward')
    done3 = d3.get('done')
    print(f'  Step(validate): reward={reward3}, done={done3}, type_reward={type(reward3).__name__}')
    
    # Check for exact 0.0, 1.0 or None
    for label, val in [('reset_reward', reward), ('skip_reward', reward2), ('validate_reward', reward3)]:
        if val is None:
            print(f'  ** WARNING: {label} is None!')
        elif val == 0.0:
            print(f'  ** WARNING: {label} is exactly 0.0!')
        elif val == 1.0:
            print(f'  ** WARNING: {label} is exactly 1.0!')
    print()
