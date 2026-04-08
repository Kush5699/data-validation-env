import copy
import random
from typing import Any, Dict, List, Tuple


def _generate_task_easy(seed: int = 42) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    rng = random.Random(seed)

    ground_truth = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 30, "department": "Engineering"},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "age": 25, "department": "Marketing"},
        {"id": 3, "name": "Carol Williams", "email": "carol@example.com", "age": 35, "department": "Engineering"},
        {"id": 4, "name": "David Brown", "email": "david@example.com", "age": 28, "department": "Sales"},
        {"id": 5, "name": "Eve Davis", "email": "eve@example.com", "age": 32, "department": "Marketing"},
    ]

    dirty = copy.deepcopy(ground_truth)
    errors = []

    missing_configs = [
        (1, "email", ""),
        (2, "department", ""),
        (4, "name", ""),
    ]

    for row_idx, field, replacement in missing_configs:
        dirty[row_idx][field] = replacement
        errors.append({
            "error_type": "missing",
            "row": row_idx,
            "field": field,
            "current_value": replacement,
            "description": f"Row {row_idx}: '{field}' is missing/empty"
        })

    return dirty, ground_truth, errors


def _generate_task_medium(seed: int = 42) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    rng = random.Random(seed)

    ground_truth = [
        {"id": 1, "product": "Laptop Pro", "price": 999.99, "quantity": 50, "sku": "LP-001", "category": "Electronics"},
        {"id": 2, "product": "Wireless Mouse", "price": 29.99, "quantity": 200, "sku": "WM-002", "category": "Accessories"},
        {"id": 3, "product": "USB Cable", "price": 9.99, "quantity": 500, "sku": "UC-003", "category": "Accessories"},
        {"id": 4, "product": "Monitor 27in", "price": 449.99, "quantity": 30, "sku": "MN-004", "category": "Electronics"},
        {"id": 5, "product": "Keyboard", "price": 79.99, "quantity": 150, "sku": "KB-005", "category": "Accessories"},
        {"id": 6, "product": "Headphones", "price": 149.99, "quantity": 80, "sku": "HP-006", "category": "Audio"},
        {"id": 7, "product": "Webcam HD", "price": 59.99, "quantity": 120, "sku": "WC-007", "category": "Electronics"},
    ]

    dirty = copy.deepcopy(ground_truth)
    errors = []

    dirty[0]["price"] = "999.99"
    errors.append({
        "error_type": "type",
        "row": 0,
        "field": "price",
        "current_value": "999.99",
        "expected_type": "float",
        "description": "Row 0: 'price' should be float, got string '999.99'"
    })

    dirty[2]["quantity"] = "five hundred"
    errors.append({
        "error_type": "type",
        "row": 2,
        "field": "quantity",
        "current_value": "five hundred",
        "expected_type": "int",
        "description": "Row 2: 'quantity' should be int, got string 'five hundred'"
    })

    dirty[3]["sku"] = "mn004"
    errors.append({
        "error_type": "format",
        "row": 3,
        "field": "sku",
        "current_value": "mn004",
        "expected_format": "XX-NNN",
        "description": "Row 3: 'sku' should match format 'XX-NNN', got 'mn004'"
    })

    dirty[5]["category"] = ""
    errors.append({
        "error_type": "missing",
        "row": 5,
        "field": "category",
        "current_value": "",
        "description": "Row 5: 'category' is missing/empty"
    })

    dirty[4]["price"] = -79.99
    errors.append({
        "error_type": "range",
        "row": 4,
        "field": "price",
        "current_value": -79.99,
        "description": "Row 4: 'price' is negative (-79.99), should be positive"
    })

    dirty[6]["sku"] = "WM-002"
    errors.append({
        "error_type": "duplicate",
        "row": 6,
        "field": "sku",
        "current_value": "WM-002",
        "description": "Row 6: 'sku' value 'WM-002' duplicates row 1"
    })

    return dirty, ground_truth, errors


def _generate_task_hard(seed: int = 42) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    rng = random.Random(seed)

    ground_truth = [
        {"id": 1, "customer": "Acme Corp", "email": "orders@acme.com", "amount": 1500.00, "currency": "USD", "status": "completed", "date": "2024-03-15", "region": "North America", "priority": "high"},
        {"id": 2, "customer": "GlobalTech", "email": "sales@globaltech.io", "amount": 2300.50, "currency": "EUR", "status": "pending", "date": "2024-03-16", "region": "Europe", "priority": "medium"},
        {"id": 3, "customer": "DataFlow Inc", "email": "info@dataflow.com", "amount": 750.00, "currency": "USD", "status": "completed", "date": "2024-03-17", "region": "North America", "priority": "low"},
        {"id": 4, "customer": "NexGen Labs", "email": "contact@nexgen.co", "amount": 4200.00, "currency": "GBP", "status": "shipped", "date": "2024-03-18", "region": "Europe", "priority": "high"},
        {"id": 5, "customer": "SwiftServe", "email": "hello@swiftserve.com", "amount": 890.25, "currency": "USD", "status": "pending", "date": "2024-03-19", "region": "Asia Pacific", "priority": "medium"},
        {"id": 6, "customer": "CloudNine", "email": "team@cloudnine.dev", "amount": 3100.00, "currency": "EUR", "status": "completed", "date": "2024-03-20", "region": "Europe", "priority": "high"},
        {"id": 7, "customer": "PeakTech", "email": "support@peaktech.com", "amount": 560.00, "currency": "USD", "status": "cancelled", "date": "2024-03-21", "region": "North America", "priority": "low"},
        {"id": 8, "customer": "Quantum AI", "email": "admin@quantumai.org", "amount": 6750.00, "currency": "USD", "status": "completed", "date": "2024-03-22", "region": "North America", "priority": "high"},
        {"id": 9, "customer": "EcoSmart", "email": "green@ecosmart.co", "amount": 1200.00, "currency": "AUD", "status": "shipped", "date": "2024-03-23", "region": "Asia Pacific", "priority": "medium"},
        {"id": 10, "customer": "BlueOcean", "email": "info@blueocean.net", "amount": 980.75, "currency": "USD", "status": "pending", "date": "2024-03-24", "region": "North America", "priority": "low"},
    ]

    dirty = copy.deepcopy(ground_truth)
    errors = []

    dirty[0]["email"] = ""
    errors.append({"error_type": "missing", "row": 0, "field": "email", "current_value": "", "description": "Row 0: 'email' is missing"})

    dirty[1]["amount"] = -2300.50
    errors.append({"error_type": "range", "row": 1, "field": "amount", "current_value": -2300.50, "description": "Row 1: 'amount' is negative"})

    dirty[2]["date"] = "03/17/2024"
    errors.append({"error_type": "format", "row": 2, "field": "date", "current_value": "03/17/2024", "expected_format": "YYYY-MM-DD", "description": "Row 2: 'date' wrong format, expected YYYY-MM-DD"})

    dirty[3]["amount"] = "4200"
    errors.append({"error_type": "type", "row": 3, "field": "amount", "current_value": "4200", "expected_type": "float", "description": "Row 3: 'amount' should be float, got string"})

    dirty[4]["status"] = "in-progress"
    errors.append({"error_type": "format", "row": 4, "field": "status", "current_value": "in-progress", "expected_format": "one of: completed, pending, shipped, cancelled", "description": "Row 4: 'status' invalid value 'in-progress'"})

    dirty[5]["region"] = ""
    errors.append({"error_type": "missing", "row": 5, "field": "region", "current_value": "", "description": "Row 5: 'region' is missing"})

    dirty[6]["customer"] = "Acme Corp"
    dirty[6]["email"] = "orders@acme.com"
    errors.append({"error_type": "duplicate", "row": 6, "field": "customer", "current_value": "Acme Corp", "description": "Row 6: 'customer' duplicates row 0"})

    dirty[7]["amount"] = 99999.99
    errors.append({"error_type": "range", "row": 7, "field": "amount", "current_value": 99999.99, "description": "Row 7: 'amount' exceeds maximum threshold (should be 6750.00)"})

    dirty[8]["currency"] = "AUSD"
    errors.append({"error_type": "format", "row": 8, "field": "currency", "current_value": "AUSD", "expected_format": "3-letter ISO code", "description": "Row 8: 'currency' invalid code 'AUSD'"})

    dirty[9]["priority"] = ""
    errors.append({"error_type": "missing", "row": 9, "field": "priority", "current_value": "", "description": "Row 9: 'priority' is missing"})

    return dirty, ground_truth, errors


TASK_REGISTRY = {
    "easy_missing_values": {
        "generator": _generate_task_easy,
        "name": "easy_missing_values",
        "description": "Fix missing values in a small employee dataset. Each empty field needs to be filled with the correct value.",
        "difficulty": "easy",
        "max_steps": 10,
        "hint": "Look for empty string values in the dataset. Use 'fix_missing' action with target_field and new_value to fill them in. Check the errors_found list for all issues."
    },
    "medium_mixed_errors": {
        "generator": _generate_task_medium,
        "name": "medium_mixed_errors",
        "description": "Fix type errors, format issues, missing values, range violations, and duplicates in a product inventory dataset.",
        "difficulty": "medium",
        "max_steps": 15,
        "hint": "Multiple error types: use fix_type for wrong data types, fix_format for pattern mismatches, fix_missing for empty fields, fix_range for out-of-bound values, and fix_duplicate for duplicate entries."
    },
    "hard_multi_constraint": {
        "generator": _generate_task_hard,
        "name": "hard_multi_constraint",
        "description": "Clean a complex customer orders dataset with 10 interrelated errors spanning missing data, type mismatches, format violations, range errors, and duplicates. Requires planning to resolve dependencies.",
        "difficulty": "hard",
        "max_steps": 20,
        "hint": "This dataset has 10 errors across 10 rows. Examine each error carefully. Some errors may need specific domain knowledge (e.g., valid statuses are: completed, pending, shipped, cancelled)."
    },
}


def get_task_names() -> List[str]:
    return list(TASK_REGISTRY.keys())


def generate_task(task_name: str, seed: int = 42) -> Dict[str, Any]:
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Unknown task: {task_name}. Available: {get_task_names()}")

    task_info = TASK_REGISTRY[task_name]
    dirty, ground_truth, errors = task_info["generator"](seed)

    return {
        "name": task_info["name"],
        "description": task_info["description"],
        "difficulty": task_info["difficulty"],
        "max_steps": task_info["max_steps"],
        "hint": task_info["hint"],
        "dataset": dirty,
        "ground_truth": ground_truth,
        "errors": errors,
        "field_names": list(ground_truth[0].keys()) if ground_truth else [],
    }


def grade_action(action_type: str, target_field: str, target_row: int,
                 new_value: str, dirty_dataset: List[Dict],
                 ground_truth: List[Dict], errors: List[Dict]) -> Tuple[float, str, bool]:
    total_errors = len(errors) if errors else 1

    if action_type == "validate":
        fixed = sum(1 for e in errors if e.get("fixed", False))
        return 0.01, f"Validation: {fixed}/{total_errors} errors fixed ({fixed/total_errors*100:.0f}%)", False

    if action_type == "skip":
        return 0.01, "Skipped current action", False

    matching_error = None
    for e in errors:
        if e.get("fixed", False):
            continue
        if e["row"] == target_row and e["field"] == target_field:
            matching_error = e
            break

    if matching_error is None:
        return 0.01, f"No unfixed error at row {target_row}, field '{target_field}'", False

    action_to_error_map = {
        "fix_missing": "missing",
        "fix_type": "type",
        "fix_range": "range",
        "fix_format": "format",
        "fix_duplicate": "duplicate",
    }

    expected_error_type = action_to_error_map.get(action_type, "")
    if expected_error_type != matching_error["error_type"]:
        return 0.01, f"Wrong action type '{action_type}' for error type '{matching_error['error_type']}'", False

    gt_value = ground_truth[target_row][target_field]

    is_correct = False
    try:
        if isinstance(gt_value, float):
            is_correct = abs(float(new_value) - gt_value) < 0.01
        elif isinstance(gt_value, int):
            is_correct = int(float(new_value)) == gt_value
        else:
            is_correct = str(new_value).strip() == str(gt_value).strip()
    except (ValueError, TypeError):
        is_correct = str(new_value).strip() == str(gt_value).strip()

    if is_correct:
        matching_error["fixed"] = True
        if isinstance(gt_value, float):
            dirty_dataset[target_row][target_field] = float(new_value)
        elif isinstance(gt_value, int):
            dirty_dataset[target_row][target_field] = int(float(new_value))
        else:
            dirty_dataset[target_row][target_field] = new_value

        reward = 0.9 / total_errors
        return reward, f"Fixed: row {target_row}, field '{target_field}' -> '{new_value}'", True
    else:
        return 0.01, f"Wrong value for row {target_row}, field '{target_field}'. Got '{new_value}', expected something else.", False
