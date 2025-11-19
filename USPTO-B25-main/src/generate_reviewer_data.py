import random
import json
import numpy as np


NUM_REVIEWERS = 22

# Data from PatentBot site.
tc_rates = {
    "1610": 0.52,  # Pharmaceutical and Agricultural Compositions
    "1620": 0.66,  # Biomedicinal Chemistry
    "1630": 0.52,  # Stem cells and cell culture
    "1640": 0.57,  # Immunology
    "1650": 0.58,  # Enzymology
    "1660": 0.87,  # Asexually Reproduced Plants
    "1670": 0.60,  # Virology
    "1680": 0.56,  # Nucleic acid assay
    "1690": 0.76,  # Organometallics
    "1710": 0.66,  # Coating, Etching
    "1720": 0.70,  # Fuel Cells
    "1730": 0.68,  # Metallurgy
    "1740": 0.68,  # Tires
    "1750": 0.69,  # UNKNOWN (retained for realism)
    "1760": 0.72,  # Organic Chemistry
    "1770": 0.72,  # Chemical Apparatus
    "1780": 0.57,  # Miscellaneous Articles
    "1790": 0.58,  # Food, Analytical Chemistry
    "2110": 0.84,  # Computer Error Control
    "2130": 0.85,  # Memory Access
    "2150": 0.76,  # Data Bases
    "2170": 0.77,  # GUI
    "2180": 0.79,  # Computer Architecture
    "2610": 0.82,  # Computer Graphics
    "2620": 0.82,  # Selective Visual Display
    "2630": 0.90  # Digital and Optical
}


TCS = list(tc_rates.keys())

# Educational levels
EDUCATION_LEVELS = [
    "PhD", "MSc", "Bachelor's", "Doctorate (Other)", "Postdoc"
]

# GS levels
# modeled as 7-12, based on our research
gs_levels = {
    "GS-7" : 0.70,
    "GS-9" : 0.80,
    "GS-11" : 0.90,
    "GS-12" : 1.00,
    "GS-13" : 1.15,
    "GS-13 PSA" : 1.25,
    "GS-14 FSA" : 1.35
}

GS = list(gs_levels.keys())

# Load names from file (same as before)
def load_names(filename="names.txt"):
    """Load names from a text file (one name per line)"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(names)} names from '{filename}'")
        return names
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please create it.")
        return []
    except Exception as e:
        print(f" Error reading file: {e}")
        return []

# Main program
if __name__ == "__main__":
    
    NAMES = load_names("names.txt")
    
    if not NAMES:
        print("No names loaded. Exiting.")
        exit(1)

    # Ensure we have at least a certain number of names
    if len(NAMES) < NUM_REVIEWERS:
        print(f"Only {len(NAMES)} names available. Using only first {NUM_REVIEWERS} names.")
        NAMES = NAMES[:NUM_REVIEWERS]
    else:
        print(f"Using first {NUM_REVIEWERS} names from list.")

    reviewer_data = []

    for i in range(NUM_REVIEWERS):
        name = random.choice(NAMES)
        tc = random.choice(TCS)  
        education = random.choice(EDUCATION_LEVELS)
        gs = random.choice(GS)
        gs_rate = gs_levels[gs]
        base_rate = tc_rates[tc]
        
        # Generate current rate (within ±5% of base rate, clamped to [0.1, 0.9])
        current_rate = round(random.uniform(base_rate - 0.05, base_rate + 0.05), 2)
        if current_rate < 0.1:
            current_rate = 0.1
        elif current_rate > 0.9:
            current_rate = 0.9

        # Generate past rate (within ±10% of current rate, clamped to [0.1, 0.9])
        past_rate = round(random.uniform(max(0.1, current_rate - 0.1), min(0.9, current_rate + 0.1)), 2)
        
        # Generate consistency score 
        consistency_score = round(random.uniform(0.3, 0.9), 2)
        
        reviewer_score = {
            "reviewer_id": f"R-{i+1:02d}",
            "reviewer_name": name,
            "tc": tc,  
            "gs": gs,
            "gs rate" : gs_rate,
            "educational_level": education,
            "current_rate": current_rate,
            "past_rate": past_rate,
            "consistency_score": consistency_score,
        }
        
        reviewer_data.append(reviewer_score)

    # Output to JSON
    output_file = "reviewer_scores.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(reviewer_data, f, indent=4)

    print(f"Generated {NUM_REVIEWERS} records in '{output_file}'")

