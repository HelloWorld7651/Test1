# Table of Contents

- `names.txt` : names used for generating reviewers
- `generate_reviewer_data.py` : script used to create reviewer data, including allowance rates, based on their TC membership. creates `reviewer_scores.json`. 
- `generate_patent_event_data.py` : script used to create patent events, containing the link of reviewer to a given patent event, while also measuring factors of risk related to the patent itself (outlined in apendix). creates `patent_events.json`

- ``nn_predict_risk.ipynb`` : jupyter notebook for training the neural net. Used to create `model_summary_high_risk.json` which denotes the top predicted highest risk TCs as well as reviewers

- ``app.py`` : flask app for displaying a dashboard, showing a visualization of risk data, in a meaningful way.

# Usage:
- 1) Generate Reviewer Data:
```
python3 generate_reviewer_data.py
```

- 2) Generate Patent Event Data:

```
python3 generate_patent_event_data.py
```

- 3) Train Prediction Model : run all code blocks in ``nn_predict_risk.ipynb``

- 4) (Optional) View Data in Dashboard

```
python3 app.py
```


# Appendix:

- A : Schema for Patent Event
```
 {
        "patent_id": "P-9669",
        "patent_type": "Industrial Application",
        "technology_domain": "Fintech",
        "TC": "3620",
        "claim_number": "39",
        "event_date": "2025-10-22T10:37:24.205043",
        "events_in_patent_history": "39",
        "time_to_first_office_action": "361.53",
        "linked_reviewers": [
            "R-01",
            "R-02"
        ],
        "reviewer_risk_contributions": [
            {
                "reviewer_id": "R-01",
                "current_rate": 0.65,
                "past_rate": 0.6,
                "consistency_score": 0.51,
                "risk_contribution": 0.587
            },
            {
                "reviewer_id": "R-02",
                "current_rate": 0.65,
                "past_rate": 0.6,
                "consistency_score": 0.51,
                "risk_contribution": 0.587
            }
        ],
 }
```