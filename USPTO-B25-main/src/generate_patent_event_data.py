import json
import random
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
from statistics import mean

# ========== FILE PATHS ==========
SIM_JSON_PATH = "patent_similarity.json"   # output from TF-IDF similarity pass
SRC_CSV_PATH = "combined.csv"              # our franken-dataset csv
OUT_SUMMARY_CSV = "patent_similarity_summary.csv"  # flat table for inspection (putting this as a failsafe)
REVIEWERS_JSON = "reviewer_scores.json"    # existing reviewer scores
EVENTS_OUT = "patent_events.json"          # output file for generated events

# ========== CONFIGURATION ==========
NUM_PATENT_EVENTS = 10000   # number of events to generate
START_INDEX = 0        # start at a given ID

PATENT_TYPES = [
    "Invention", "Design", "Utility", "Plant", "Industrial Application"
]
TECHNOLOGY_DOMAINS = [
    "AI/ML", "NLP", "Robotics", "Biotech", "Pharmaceuticals", "Cryptography",
    "Quantum Computing", "Computer Vision", "Hardware", "Fintech"
]

AVERAGE_TIME_TO_COMPLETION = 20 # average end2end time for complete patent event.

# ========== WEIGHTS CONFIG ==========
REVIEWER_SCORE_WEIGHTS = {
    "current_rate": 0.4,
    "past_rate": 0.3,
    "consistency_score": 0.3
    #"time : ???
}

SIM_SCORE_WEIGHT = 0.7
COMPLEXITY_SCORE_WEIGHT = 0.3

SEARCH_DEPTH_WEIGHT = 0.6
SEARCH_DURATION_WEIGHT = 0.4

# ========== WEIGHTS CONFIG ==========
RISK_THRESHOLDS = {
    "low": 0.15,
    "medium": 0.25,
    "high": 0.35
}

# === REAL TC MAPPING (using your actual 4-digit sub-TCs) ===
REAL_TC_MAP = {
    "Chemistry" : 1600,
    "Electrical engineering" : 2800,
    "Instruments" : 3600,
    "Mechanical engineering" : 3700,
    "Other fields" : 0000,
}
TC_FALLBACK = "1600"

# adding TC differential
TC_TIME_DIFFERENTIAL = {
    1600 : 3,
    2800 : 6,
    3600 : -2,
    3700 : 4,
    0000 : 0
}


# Time to first office action (in days)
TIME_TO_FIRST_OFFICE_ACTION = {
    "Invention": 365,
    "Design": 180,
    "Utility": 120,
    "Plant": 270,
    "Industrial Application": 450
}



# ========== SIMILARITY PARSING + AGGREGATION ==========

def load_similarity(sim_json_path=SIM_JSON_PATH):
    """Load and parse patent similarity JSON data."""
    with open(sim_json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_id_map(csv_path):
    """
    Load and clean the ID mapping DataFrame with tech columns.
    Returns a DataFrame containing:
        - 'patent_id' (unique identifier)
        - 'patent_number_like' (normalized patent number)
        - 'first_wipo_sector_title' (Wipo sector title, if available)
        - 'first_wipo_field_title' (Wipo field title, if available)
    """
    # Critical fix: low_memory=False prevents mixed-type slowdowns
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Step 1: Find patent ID column (case-insensitive pattern matching)
    patent_id_col = None
    for col in df.columns:
        if any([word in col.lower() for word in ['patent', 'id', 'pid']]):
            patent_id_col = col
            break
    if patent_id_col is None:
        raise ValueError("No patent ID column found. Check column names.")
    
    # Step 2: Find patent number column (preferred patterns)
    patent_number_col = None
    preferred_patterns = ['patent_number', 'publication_number', 'pub_number', 
                          'grant_number', 'number', 'patent']
    for col in preferred_patterns:
        if col in df.columns:
            patent_number_col = col
            break
    if patent_number_col is None:
        # Fallback: use first column with 'patent' in name
        for col in df.columns:
            if 'patent' in col.lower():
                patent_number_col = col
                break
        if patent_number_col is None:
            raise ValueError("No patent number column found. Check column names.")
    
    new_df = df[[patent_id_col, patent_number_col]]
    new_df.columns = ['patent_id', 'patent_number_like']
    
    if 'first_wipo_sector_title' in df.columns:
        new_df['first_wipo_sector_title'] = df['first_wipo_sector_title'].astype(str).copy()
    if 'first_wipo_field_title' in df.columns:
        new_df['first_wipo_field_title'] = df['first_wipo_field_title'].astype(str).copy() 
    
    # Step 5: Drop duplicates (keep first occurrence)
    return new_df.drop_duplicates(subset=['patent_id'], keep='first')

def compute_similarity_averages(sim_data):
    """
    Build:
      sim_stats: {
        patent_id: {
          'per_claim_avg': { claim_number: avg(float) },
          'patent_avg': avg across claim avgs (float or NaN)
        }
      }
    Also returns flat_rows (one row per claim) for optional CSV export.
    """
    sim_stats = {}
    flat_rows = []

    for patent_id, claims in sim_data.items():
        per_claim = {}
        for entry in claims:
            claim_no = entry.get("claim_number")
            sims = [
                x.get("similarity_score")
                for x in entry.get("top_3_similar", [])
                if x.get("similarity_score") is not None
            ]
            if sims:
                avg_claim = float(mean(sims))
                per_claim[str(claim_no)] = avg_claim
                flat_rows.append({
                    "patent_id": str(patent_id),
                    "claim_number": str(claim_no),
                    "claim_avg_similarity": avg_claim
                })

        patent_avg = float(mean(per_claim.values())) if per_claim else float("nan")

        sim_stats[str(patent_id)] = {
            "per_claim_avg": per_claim,
            "patent_avg": patent_avg
        }

    return sim_stats, flat_rows

def main_build_similarity_summary():
    sim_data = load_similarity(SIM_JSON_PATH)
    id_map_df = load_id_map(SRC_CSV_PATH)
    sim_stats, flat_rows = compute_similarity_averages(sim_data)

    # Optional: write a tidy CSV for inspection
    if flat_rows:
        claim_level_df = pd.DataFrame(flat_rows)
        claim_level_df = claim_level_df.merge(id_map_df, on="patent_id", how="left")
        claim_level_df["patent_avg_similarity"] = claim_level_df["patent_id"].map(
            lambda pid: sim_stats.get(pid, {}).get("patent_avg")
        )
        claim_level_df.sort_values(by=["patent_id", "claim_number"], inplace=True, key=lambda s: s.astype(str))
        claim_level_df.to_csv(OUT_SUMMARY_CSV, index=False)
        print(f"✓ Wrote claim-level summary to {OUT_SUMMARY_CSV} ({len(claim_level_df)} rows)")
    else:
        print("No claim-level rows to write (possibly no matches).")

    return sim_stats, id_map_df

# ========== REVIEWER DATA LOADING ==========

def load_reviewers(filename=REVIEWERS_JSON):
    """Load and validate reviewer data."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} reviewers from '{filename}'")
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please run generate_reviewer_data.py first.")
        return []
    except Exception as e:
        print(f"Error loading reviewers: {e}")
        return []

# ========== ORDERED PATENT IDS  ==========
SIM_STATS = None
ID_MAP_DF = None
ORDERED_PATENT_IDS = []  # preserve dataset order

def prepare_ordered_patent_ids(id_map_df):
    """Return ordered patent IDs exactly as they first appear in the dataset."""
    return list(id_map_df["patent_id"].drop_duplicates(keep="first").astype(str))

def get_patent_number_like(patent_id, id_map_df):
    """Return human-friendly patent number if present; else the patent_id."""
    if id_map_df is None or id_map_df.empty:
        return patent_id
    row = id_map_df.loc[id_map_df["patent_id"] == str(patent_id)]
    if row.empty:
        return patent_id
    val = row.iloc[0]["patent_number_like"]
    return val if pd.notna(val) and str(val).strip() else patent_id

# ========== GENERATE ONE PATENT EVENT (WITH EXPLICIT PID) ==========

def generate_patent_event(reviewer_data, pid):
    """
    Generate one patent event where:
      - 'similarity_metrics.per_claim_average_similarity' lists per-claim averages
      - 'patent_risk_contributions[0].patent_claim_average_similarity' is the patent average
    """
    if SIM_STATS is None or not SIM_STATS:
        raise RuntimeError("SIM_STATS not loaded.")
    if pid not in SIM_STATS:
        raise ValueError(f"Patent id '{pid}' not found in similarity stats.")

    patent_number_like = get_patent_number_like(pid, ID_MAP_DF)

    tech_domain_dict = ID_MAP_DF.set_index('patent_id')['first_wipo_sector_title'].to_dict()
    tech_field_dict = ID_MAP_DF.set_index('patent_id')['first_wipo_field_title'].to_dict()

    tech_domain = tech_domain_dict.get(pid, None)
    tech_field = tech_field_dict.get(pid, None)
    
    tc = REAL_TC_MAP.get(tech_domain, TC_FALLBACK)

    # parse claims from the DB, increment the amount of claims that each ID has.

    search_duration = f"{random.uniform(1.0, 45.0):.2f}"
    search_depth = random.randint(10, 100)
    end_search_date = (datetime.now() - timedelta(days=random.uniform(1, 45))).isoformat()

    # ==== BS CODE ====

    # Reviewer time for prior art (hrs)
    prior_search_hrs = round(random.uniform(6.0, 16.0), 2)
    review_hrs = round(random.uniform(3.0, 13.0), 2)

    total_time_spent = prior_search_hrs + review_hrs

    # ==== BS CODE ====

    # Compute search complexity index (Between 0 and 1)
    search_complexity = SEARCH_DEPTH_WEIGHT * (float(search_depth) / 100) + SEARCH_DURATION_WEIGHT * (float(search_duration) / 45)
    search_complexity = min(max(search_complexity, 0), 1) # clamp 0-1

    # NOT USEFUL ANYMORE
    # Expected time (6-16 hrs scaled by complexity)
    # Simple search (SCI = 0.0) -> 6 hrs
    # Deep/Long Search (SCI 1.0) -> 16 hrs
    # expected_time = 6 + (10 * search_complexity)
    
    # NOT USEFUL ANYMORE ?
    # Time deviation risk (difference from expected)
    # Near 0 = efficient (close to expected)
    # Higher = inefficient or rushed?
    # time_deviation = abs(hours_spent - expected_time) / expected_time
    # time_efficiency_risk = min(time_deviation, 1.0)

    # ==== BS CODE ====

    # Reviewers
    selected_reviewers = random.choices(
        [r["reviewer_id"] for r in reviewer_data],
        weights=[r.get("current_rate", 0.0) * 10 for r in reviewer_data],
        k=random.randint(1, 3)
    )
    total_risk, reviewer_count = 0.0, 0
    reviewer_rows = []
    for reviewer_id in selected_reviewers:
        reviewer = next((r for r in reviewer_data if r["reviewer_id"] == reviewer_id), None)
        if not reviewer:
            continue
        # Get reviewer scores
        current = reviewer.get("current_rate", 0.0)
        past = reviewer.get("past_rate", 0.0)
        consistency = reviewer.get("consistency_score", 0.0)
        
        # Calculate risk (0-1) for this reviewer - lower = less risk
        risk_contrib = (
            (1 - current) * REVIEWER_SCORE_WEIGHTS["current_rate"] +  # Lower current = higher risk
            (1 - past) * REVIEWER_SCORE_WEIGHTS["past_rate"] +      # Lower past = higher risk
            (1 - consistency) * REVIEWER_SCORE_WEIGHTS["consistency_score"]  # Lower consistency = higher risk
            # time_efficiency_risk * REVIEWER_SCORE_WEIGHTS["time_efficiency"]
        )

        # Time Risk Calculations (GS here): 
        tc_time_diff = TC_TIME_DIFFERENTIAL.get(tc)
        gs_rate = reviewer.get("gs rate", 0.0)

        reviewer_expected_time = (AVERAGE_TIME_TO_COMPLETION + tc_time_diff ) / gs_rate

        # TODO: Implement comparison between reviwer expected time and total time spent. Then compare risk in terms 
        # of distance from time spent to expected time, both high and low.

        time_difference = abs(total_time_spent - reviewer_expected_time) 
        proportional_risk = time_difference / reviewer_expected_time
        time_risk = min (1.0, proportional_risk)
        

        reviewer_rows.append({
            "reviewer_id": reviewer_id,
            "current_rate": current,
            "past_rate": past,
            "reviewer_expected_time": reviewer_expected_time, # added Reviewer's expected time.
            "reviwer_time_risk" : time_risk,
            "consistency_score": consistency,
            "risk_contribution": risk_contrib
        })
        total_risk += risk_contrib # TODO, UPDATE TO REFLECT ACTUAL RISK CALCULATION
        reviewer_count += 1

    risk_score = (total_risk / reviewer_count) if reviewer_count else 0.0
    if risk_score >= RISK_THRESHOLDS["high"]:
        risk_label = "High"
    elif risk_score >= RISK_THRESHOLDS["medium"]:
        risk_label = "Medium"
    else:
        risk_label = "Low"

    # Similarity metrics (parsed)
    sim_info = SIM_STATS.get(str(pid), {})
    per_claim_avg = sim_info.get("per_claim_avg", {})
    total_claims = len(per_claim_avg)
    patent_avg = sim_info.get("patent_avg", float("nan"))

    # Sort per-claim list by numeric claim number if possible
    def _claim_sort_key(k):
        try:
            return int(k)
        except:
            return k

    per_claim_list = [
        {"claim_number": str(cn), "avg_similarity": round(float(avg), 4)}
        for cn, avg in sorted(per_claim_avg.items(), key=lambda kv: _claim_sort_key(kv[0]))
    ]

    patent_claim_average_similarity = None if pd.isna(patent_avg) else round(float(patent_avg), 4)

    # Composite (example) using patent-level similarity & a complexity draw
    complexity_score = round(random.uniform(0.1, 0.4), 2)
    composite_similarity_risk = round(
        (SIM_SCORE_WEIGHT * (patent_claim_average_similarity if patent_claim_average_similarity is not None else 0.0))
        + (COMPLEXITY_SCORE_WEIGHT* complexity_score),
        3
    )

    event = {
        "patent_id": str(pid),
        "technology_domain": tech_domain,
        "tech_field": tech_field,
        "TC": tc,
        "number_of_claims": total_claims,
        "search_duration": search_duration,
        "search_depth": str(search_depth),
        "reviewer_time_hours": total_time_spent,
        "end_search_date": end_search_date,
         # "time_efficiency_risk": round(time_efficiency_risk, 3),

        "linked_reviewers": selected_reviewers,
        "reviewer_risk_contributions": reviewer_rows,

        "patent_risk_contributions": [
            {
                "patent_claim_average_similarity": patent_claim_average_similarity,
                "complexity_score": complexity_score,
                "composite_risk_score": composite_similarity_risk,
                "risk_label": risk_label,
                "source": "synthetic_event"
            }
        ],

        "composite_risk_score": round(risk_score, 3),
        "risk_label": risk_label,

        "similarity_metrics": {
            "per_claim_average_similarity": per_claim_list,
            "patent_average_similarity": patent_claim_average_similarity,
            "source": "parsed_from_similarity_json"
        },

        "source": "synthetic_event"
    }
    return event

# ========== MAIN SCRIPT ==========

if __name__ == "__main__":
    # Step 0: Build similarity summary and ID map
    try:
        SIM_STATS, ID_MAP_DF = main_build_similarity_summary()
        if not SIM_STATS:
            print("No similarity stats loaded from JSON. Exiting.")
            raise SystemExit(1)
        print(f"✅ Loaded similarity stats for {len(SIM_STATS)} patents.")
    except Exception as e:
        print(f"Error preparing similarity stats: {e}")
        raise SystemExit(1)

    # Step 1: Load reviewers
    reviewers = load_reviewers(REVIEWERS_JSON)
    if not reviewers:
        print("No reviewers loaded. Exiting.")
        raise SystemExit(1)

    # Step 2: Prepare ordered patent IDs (sequential by dataset order)
    ORDERED_PATENT_IDS = prepare_ordered_patent_ids(ID_MAP_DF)
    print(f"Found {len(ORDERED_PATENT_IDS)} unique patent IDs in dataset order.")

    # Bounds for sequential slice
    end_index = min(START_INDEX + NUM_PATENT_EVENTS, len(ORDERED_PATENT_IDS))
    if START_INDEX >= len(ORDERED_PATENT_IDS) or START_INDEX < 0:
        print("START_INDEX out of range for available patents.")
        raise SystemExit(1)

    print(f"Generating {end_index - START_INDEX} patent event(s) from index {START_INDEX} to {end_index - 1}...")

    # Step 3: Sequential generation
    patent_events = []
    for i in range(START_INDEX, end_index):
        pid = ORDERED_PATENT_IDS[i]
        if pid not in SIM_STATS:
            # skip patents missing in similarity JSON
            continue
        event = generate_patent_event(reviewers, pid)
        patent_events.append(event)

    # Step 4: Save
    with open(EVENTS_OUT, "w", encoding="utf-8") as f:
        json.dump(patent_events, f, indent=4)

    print(f"Generated {len(patent_events)} sequential synthetic patent event(s) in '{EVENTS_OUT}'")
    if patent_events:
        print("Sample event:")
        print(json.dumps(patent_events[0], indent=4))
