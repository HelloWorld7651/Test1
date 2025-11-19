import pandas as pd
import numpy as np
import json
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# start time
overall_start = time.perf_counter()

def default(obj):
    """JSON-safe default for numpy types"""
    if isinstance(obj, np.integer):
        return int(obj.item())
    elif isinstance(obj, np.floating):
        return float(obj.item())
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def preprocess_text(text):
    """Minimal, memory-efficient preprocessing"""
    return text.lower().strip() if pd.notna(text) else ""

#
df = pd.read_csv('combined.csv', nrows = 200000)

df['clean_text'] = df['claim_text'].apply(preprocess_text)


cpc_groups = df.groupby('cpc_sections')

output_dict = {}
total_claims = 0

for cpc_group, group_df in cpc_groups:
    group = group_df.reset_index(drop=True)
    if len(group) < 2:
        continue

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(group['clean_text'])

    sim_mat = cosine_similarity(tfidf_matrix)
    n = len(group)

    # Precompute patent ids as a numpy array for fast masking
    patent_ids = group['patent_id'].to_numpy()

    for pos, row in group.iterrows():
        scores = sim_mat[pos].copy()

        # Mask out all claims from the SAME patent (including the current one)
        same_patent_mask = (patent_ids == row['patent_id'])
        scores[same_patent_mask] = -1.0  # ensures they won't be selected

        # Take top 3 from remaining (other patents only)
        # Filter invalids, then argsort descending
        valid_idx = np.where(scores >= 0)[0]
        if valid_idx.size == 0:
            top_indices = []
        else:
            top_indices = valid_idx[np.argsort(scores[valid_idx])[::-1][:3]]

        results = []
        for j in top_indices:
            results.append({
                "patent_number": group.iloc[j]['patent_id'],
                "claim_number": group.iloc[j]['claim_sequence'],
                "similarity_score": round(float(scores[j]), 4)
            })

        pid = row['patent_id']
        if pid not in output_dict:
            output_dict[pid] = []
        output_dict[pid].append({
            "claim_number": row['claim_sequence'],
            "top_3_similar": results
        })
        total_claims += 1


overall_time = time.perf_counter() - overall_start

with open('patent_similarity.json', 'w') as f:
    json.dump(output_dict, f, indent=2, default=default)

print(f"Total processing time: {overall_time:.4f} seconds")
print("Output saved to 'patent_similarity.json'")
print(f"Total claims processed: {total_claims}")
if output_dict:
    first_key = next(iter(output_dict))
    print(f"Sample output: {output_dict[first_key][:2]}")
else:
    print("Sample output: (no results)")
