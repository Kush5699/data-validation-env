import time, requests
from huggingface_hub import HfApi
api = HfApi()
for i in range(20):
    info = api.space_info("kush5699/data-validation-env")
    stage = info.runtime.stage if info.runtime else "UNKNOWN"
    print(f"[{i}] {stage}")
    if stage == "RUNNING":
        r = requests.post("https://kush5699-data-validation-env.hf.space/reset", json={"task_name":"easy_missing_values","seed":42}, timeout=30)
        obs = r.json()
        print(f"  Reward on reset: {obs['reward']}")
        r2 = requests.post("https://kush5699-data-validation-env.hf.space/step", json={"action_type":"fix_missing","target_field":"email","target_row":1,"new_value":"bob@example.com"}, timeout=30)
        obs2 = r2.json()
        print(f"  Step reward: {obs2['reward']}")
        print(f"  Cumulative: {obs2['cumulative_reward']}")
        print(f"  In (0,1): {0 < obs2['reward'] < 1 and 0 < obs2['cumulative_reward'] < 1}")
        break
    if "ERROR" in stage: break
    time.sleep(10)
