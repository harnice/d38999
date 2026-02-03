import os
import sys
import csv
from datetime import datetime
from pathlib import Path
import json

# Add parent directory to path to import d38999_specs
sys.path.insert(0, str(Path(__file__).parent.parent))
from d38999_specs import d38999_specs

CURRENT_REV = 1

# Part configurations to render
PART_CONFIGS = [
    "26,Z,A,98,P,N",
    "26,Z,A,98,P,A",
]

COLUMNS = [
    "product",
    "mfg",
    "pn",
    "desc",
    "rev",
    "status",
    "releaseticket",
    "library_repo",
    "library_subpath",
    "datestarted",
    "datemodified",
    "datereleased",
    "git_hash_of_harnice_src",
    "drawnby",
    "checkedby",
    "revisionupdates",
    "affectedinstances",
]


def format_part_number_for_dir(part_config):
    """Convert part config to directory name format."""
    parts = part_config.split(',')
    return f"D38999_{''.join(parts)}"


def format_part_number_for_parsing(part_config):
    """Convert part config to D38999/26ZA98PN format."""
    parts = part_config.split(',')
    return f"D38999/{''.join(parts)}"


def ensure_part_directory(part_dir):
    """Create part directory if it doesn't exist."""
    if not os.path.exists(part_dir):
        os.makedirs(part_dir)
        print(f"Created directory: {part_dir}")


def get_revision_history_path(part_dir, part_number):
    """Get path to revision history CSV."""
    clean_pn = part_number.replace('/', '_')
    return os.path.join(part_dir, f"{clean_pn}-revision_history.csv")


def read_revision_history(csv_path):
    """Read existing revision history CSV."""
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_revision_history(csv_path, rows):
    """Write revision history CSV."""
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def update_revision_row(rows, part_number, current_rev):
    """Update or append revision row."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    new_row = {col: "" for col in COLUMNS}
    new_row.update({
        "product": part_number,
        "pn": part_number,
        "rev": str(current_rev),
        "datemodified": today,
    })
    
    # Check if revision already exists
    rev_exists = False
    for i, row in enumerate(rows):
        if row.get("rev") == str(current_rev):
            # Preserve datestarted if it exists
            if row.get("datestarted"):
                new_row["datestarted"] = row["datestarted"]
            else:
                new_row["datestarted"] = today
            rows[i] = new_row
            rev_exists = True
            break
    
    if not rev_exists:
        new_row["datestarted"] = today
        rows.append(new_row)
    
    return rows


def ensure_revision_directory(part_dir, part_number, current_rev):
    """Create/clear revision directory."""
    clean_pn = part_number.replace('/', '_')
    rev_dir = os.path.join(part_dir, f"{clean_pn}-rev{current_rev}")
    
    # If exists, clear contents
    if os.path.exists(rev_dir):
        for item in os.listdir(rev_dir):
            item_path = os.path.join(rev_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        print(f"Cleared contents of: {rev_dir}")
    else:
        os.makedirs(rev_dir)
        print(f"Created directory: {rev_dir}")
    
    return rev_dir


def write_attributes_json(rev_dir, part_number, part_info):
    """Write attributes JSON file."""
    clean_pn = part_number.replace('/', '_')
    json_path = os.path.join(rev_dir, f"{clean_pn}-rev{CURRENT_REV}-attributes.json")
    
    attributes = {
        "part_number": part_number,
        "revision": CURRENT_REV,
        "parsed_info": part_info,
        "generated_date": datetime.now().isoformat(),
    }
    
    with open(json_path, 'w') as f:
        json.dump(attributes, f, indent=2)
    
    print(f"Written: {json_path}")


def main():
    parser = d38999_specs.D38999Parser()
    
    for part_config in PART_CONFIGS:
        print(f"\n{'='*60}")
        print(f"Processing: {part_config}")
        print('='*60)
        
        # Format part number
        part_number = format_part_number_for_parsing(part_config)
        dir_name = format_part_number_for_dir(part_config)
        
        # Parse part number
        try:
            part_info = parser.parse_part_number(part_number)
            print(f"Parsed: {part_number}")
        except Exception as e:
            print(f"Error parsing {part_number}: {e}")
            continue
        
        # Ensure part directory exists
        part_dir = os.path.join(os.getcwd(), dir_name)
        ensure_part_directory(part_dir)
        
        # Handle revision history CSV
        csv_path = get_revision_history_path(part_dir, dir_name)
        rows = read_revision_history(csv_path)
        rows = update_revision_row(rows, dir_name, CURRENT_REV)
        write_revision_history(csv_path, rows)
        print(f"Updated: {csv_path}")
        
        # Handle revision directory
        rev_dir = ensure_revision_directory(part_dir, dir_name, CURRENT_REV)
        
        # Write attributes JSON
        write_attributes_json(rev_dir, part_number, part_info)
    
    print(f"\n{'='*60}")
    print("Processing complete!")
    print('='*60)


if __name__ == "__main__":
    main()