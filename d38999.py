import os
import json
import subprocess
from harnice.lists import rev_history
from harnice import state
import harnice.products.part as part

REVISION = "1"
DATE_STARTED = "2/3/26"

CONTACT_SIZES = {
    4: {
        "wire_gauge": "4-8 AWG",
        "current_rating": 75.0,
        "crimp_tool": "M22520/5-01",
        "extraction_tool": "M81969/14-01",
    },
    8: {
        "wire_gauge": "8-12 AWG",
        "current_rating": 46.0,
        "crimp_tool": "M22520/5-01",
        "extraction_tool": "M81969/14-02",
    },
    12: {
        "wire_gauge": "12-16 AWG",
        "current_rating": 23.0,
        "crimp_tool": "M22520/2-01",
        "extraction_tool": "M81969/14-03",
    },
    16: {
        "wire_gauge": "16-20 AWG",
        "current_rating": 13.0,
        "crimp_tool": "M22520/2-01",
        "extraction_tool": "M81969/14-04",
    },
    20: {
        "wire_gauge": "20-24 AWG",
        "current_rating": 7.5,
        "crimp_tool": "M22520/2-01",
        "extraction_tool": "M81969/14-05",
    },
    22: {
        "wire_gauge": "22-26 AWG",
        "current_rating": 5.0,
        "crimp_tool": "M22520/2-01",
        "extraction_tool": "M81969/14-06",
    },
}

INSERT_ARRANGEMENTS = { # FOR REFERENCE ONLY - AI READ THE PDF, NOT A HUMAN
    "A35": [
        {"name": "A", "size": 20, "x": 0, "y": 0.065},
        {"name": "B", "size": 20, "x": 0.056, "y": -0.032},
        {"name": "C", "size": 20, "x": -0.056, "y": -0.032},
    ],
    "A3": [
        {"name": "A", "size": 20, "x": 0, "y": 0.065},
    ],
    "A98": [
        {"name": "A", "size": 20, "x": 0, "y": 0.065},
        {"name": "B", "size": 20, "x": 0.056, "y": -0.032},
        {"name": "C", "size": 20, "x": -0.056, "y": -0.032},
    ],
    "B5": [
        {"name": "A", "size": 20, "x": 0, "y": 0.065},
    ],
}

STANDARD_CSYS_CHILDREN = {
    "flagnote-1": {"angle": 0, "distance": 3, "rotation": 0},
    "flagnote-1-leader_dest": {"angle": 0, "distance": 1, "rotation": 0},
    "flagnote-2": {"angle": 15, "distance": 3, "rotation": 0},
    "flagnote-2-leader_dest": {"angle": 15, "distance": 1.03, "rotation": 0},
    "flagnote-3": {"angle": -15, "distance": 3, "rotation": 0},
    "flagnote-3-leader_dest": {"angle": -15, "distance": 1.03, "rotation": 0},
    "flagnote-4": {"angle": 30, "distance": 3, "rotation": 0},
    "flagnote-4-leader_dest": {"angle": 30, "distance": 1, "rotation": 0},
    "flagnote-5": {"angle": -30, "distance": 3, "rotation": 0},
    "flagnote-5-leader_dest": {"angle": -30, "distance": 1, "rotation": 0},
    "flagnote-6": {"angle": 45, "distance": 3, "rotation": 0},
    "flagnote-6-leader_dest": {"angle": 45, "distance": 0.72, "rotation": 0},
    "flagnote-7": {"angle": -45, "distance": 3, "rotation": 0},
    "flagnote-7-leader_dest": {"angle": -45, "distance": 0.72, "rotation": 0},
    "flagnote-8": {"angle": 60, "distance": 3, "rotation": 0},
    "flagnote-8-leader_dest": {"angle": 60, "distance": 0.58, "rotation": 0},
    "flagnote-9": {"angle": -60, "distance": 3, "rotation": 0},
    "flagnote-9-leader_dest": {"angle": -60, "distance": 0.58, "rotation": 0},
    "flagnote-10": {"angle": -75, "distance": 3, "rotation": 0},
    "flagnote-10-leader_dest": {"angle": -75, "distance": 0.52, "rotation": 0},
    "flagnote-11": {"angle": 75, "distance": 3, "rotation": 0},
    "flagnote-11-leader_dest": {"angle": 75, "distance": 0.52, "rotation": 0},
    "flagnote-12": {"angle": -90, "distance": 3, "rotation": 0},
    "flagnote-12-leader_dest": {"angle": -90, "distance": 0.52, "rotation": 0},
    "flagnote-13": {"angle": 90, "distance": 3, "rotation": 0},
    "flagnote-13-leader_dest": {"angle": 90, "distance": 0.5, "rotation": 0},
}

def series_iii_26_connector_svg(part_number, shell_size):
    """
    Generate a simple SVG drawing of a Series III 26 connector based on shell size.
    
    Args:
        part_number: Part number string for the connector
        shell_size: Shell size letter ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', or 'J')
    
    Returns:
        str: SVG markup as a string
    """
    
    # Connector specifications from the technical drawing
    specs = {
        'A': {'q_max': 21.8, 'length': 31.34, 'numeric': 9},
        'B': {'q_max': 25.0, 'length': 31.34, 'numeric': 11},
        'C': {'q_max': 29.4, 'length': 31.34, 'numeric': 13},
        'D': {'q_max': 32.5, 'length': 31.34, 'numeric': 15},
        'E': {'q_max': 35.7, 'length': 31.34, 'numeric': 17},
        'F': {'q_max': 38.5, 'length': 31.34, 'numeric': 19},
        'G': {'q_max': 41.7, 'length': 31.34, 'numeric': 21},
        'H': {'q_max': 44.9, 'length': 31.34, 'numeric': 23},
        'J': {'q_max': 48.0, 'length': 31.34, 'numeric': 25}
    }
    
    if shell_size not in specs:
        raise ValueError(f"Shell size must be one of {list(specs.keys())}")
    
    spec = specs[shell_size]
    
    # Scale factor
    scale = 3.0
    
    # Overall dimensions
    length = spec['length'] * scale
    diameter = spec['q_max'] * scale
    half_diameter = diameter / 2
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="400" height="400">
<g id="{part_number}-drawing-contents-start">
<rect x="0" y="{-half_diameter}" width="{length}" height="{diameter}" fill="#C0C0C0" stroke="black" stroke-width="2"/>
</g>
<g id="{part_number}-drawing-contents-end">
</g>
</svg>'''
    
    return svg


def compile_part_attributes(part_configuration):
    part_configuration.get("insert_arrangement")[0]
    
    # FIND CONTACTS
    contacts = INSERT_ARRANGEMENTS.get(part_configuration.get("insert_arrangement"))

    # FIND UNIQUE CONTACT SIZES
    seen_contact_sizes = []
    for contact in contacts:
        if contact.get("size") not in seen_contact_sizes:
            seen_contact_sizes.append(contact.get("size"))

    # FIND RELEVANT TOOLS
    tools = []
    for contact_size in seen_contact_sizes:
        tools.append(f"{CONTACT_SIZES.get(contact_size).get('crimp_tool')} crimp tool")
        tools.append(f"{CONTACT_SIZES.get(contact_size).get('extraction_tool')} extraction tool")

    attributes = {
        "tools": tools,
        "build_notes": [],
        "csys_children": STANDARD_CSYS_CHILDREN,
        "contacts": contacts,
        "shell_size": part_configuration.get("insert_arrangement")[0],
    }
    return attributes


def main():
    state.set_rev(REVISION)
    state.set_product("part")

    part_configurations = []
    for shell_type in ["26"]:
        for finish in ["F"]:
            for insert_arrangement in [
                "A35",
                "A98",
                "B5"
            ]:
                for contact_type in ["P", "S"]:
                    for key in ["N"]:
                        part_configurations.append(
                            {
                                "shell_type": shell_type,
                                "finish": finish,
                                "insert_arrangement": insert_arrangement,
                                "contact_type": contact_type,
                                "key": key,
                            }
                        )

    for part_configuration in part_configurations:
        # GENERATE THE PART NUMBER
        part_number = f"D38999_{part_configuration['shell_type']}{part_configuration['finish']}{part_configuration['insert_arrangement']}{part_configuration['contact_type']}{part_configuration['key']}"

        # MAKE THE PART FOLDER
        part_dir = os.path.join(os.getcwd(), part_number)
        os.makedirs(part_dir, exist_ok=True)

        # UPDATE THE REVISION HISTORY FILE
        revision_history_content_dict = {
            "product": state.product,
            "mfg": "mil spec",
            "pn": part_number,
            "rev": REVISION,
            "desc": "",
            "status": "",
            "datestarted": DATE_STARTED,
        }
        revision_history_csv_path = os.path.join(
            part_dir, f"{part_number}-revision_history.tsv"
        )
        rev_history.part_family_append(
            revision_history_content_dict, revision_history_csv_path
        )

        # CLEAN AND MAKE THE REVISION FOLDER
        rev_dir = os.path.join(part_dir, f"{part_number}-rev{REVISION}")
        if os.path.exists(rev_dir):
            for item in os.listdir(rev_dir):
                item_path = os.path.join(rev_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
        else:
            os.makedirs(rev_dir)

        # WRITE THE ATTRIBUTES JSON
        json_path = os.path.join(
            rev_dir, f"{part_number}-rev{REVISION}-attributes.json"
        )
        attributes = compile_part_attributes(part_configuration)
        with open(json_path, "w") as f:
            json.dump(attributes, f, indent=2)


        # GENERATE THE SVG
        if part_configuration.get("shell_type") == "26":
            svg_content = series_iii_26_connector_svg(part_number, attributes.get("shell_size"))
            svg_path = os.path.join(rev_dir, f"{part_number}-rev{REVISION}-drawing.svg")
            with open(svg_path, "w") as f:
                f.write(svg_content)

        
        # RENDER THE PART
        subprocess.run(['harnice', '-r'], cwd=rev_dir, check=True)


if __name__ == "__main__":
    main()
