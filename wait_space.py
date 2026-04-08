import time
from huggingface_hub import HfApi
api = HfApi()
for i in range(30):
    info = api.space_info("kush5699/data-validation-env")
    stage = info.runtime.stage if info.runtime else "UNKNOWN"
    print(f"[{i}] {stage}")
    if stage == "RUNNING":
        print("Space is RUNNING! Safe to submit now.")
        break
    if "ERROR" in stage:
        print("ERROR! Check space logs.")
        break
    time.sleep(10)
