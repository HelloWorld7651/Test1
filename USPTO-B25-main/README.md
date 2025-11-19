# REI : A Patent Risk Evaluation Framework for the USPTO

Code for:
- Deriving Measurements of Risk
- Creating Mock data, to show factors of risk
- Predicting future risk, based on "historical" data.

# USAGE :
- See README in `/src`
# Methodology

Current Schema for "Patent Event Risk Score"

```
 {
        "patent_id": "P-7132",
        "patent_type": "Industrial Application",
        "technology_domain": "Pharmaceuticals", # This will be changed to accurately reflect real life TCs, as well as domains.
        "TC": "TC-03",
	"Claim_number": " 1", # I want to have it claim based, instead of just the entire patent at once. We will find some accurate range between 1 and inf to have the "number of claims, per given patent ID" generated.
        "event_date": "2022-09-21T11:50:49.885787", # this we could maybe go without, but it could be used for further sorting.

	# NEW SCHEMA STUFF:
	"events_in_patent_history" : "1", # We can use the claim number to count essentially. 
					# the idea is that higher num in history = more risky. Don't know til we get interviews.

	"time_to_first_office_action" : "foobar" # more risk if we leave it sitting for too long. likewise, too short could also be a risk. 
						# need to think about this one more.
        "linked_reviewers": [
            "R-02",
            "R-15"
        ],
        "reviewer_risk_contributions": [ # this will be changed to reflect acceptable rates, within the standard deviation for a TC. We don't want to put any super crazy outliers in there.
            {
                "reviewer_id": "R-02",
                "current_rate": 0.34, 
                "past_rate": 0.23,
                "consistency_score": 0.34,
                "risk_contribution": 0.403
            },
            {
                "reviewer_id": "R-15",
                "current_rate": 0.34,
                "past_rate": 0.23,
                "consistency_score": 0.34,
                "risk_contribution": 0.403
            }
        ],

	"patent_risk_contributions": [
	    {
		"similarity_score: 0.9",
		"compexity_score : 0.1" # I want to find a reasonable way to denote this. Current idea is to have it based off claim length.
		
        "composite_risk_score": 0.447, # we need to generate a formal formula for calculating the composite risk score for the given patent event.
					# likewise, we can take these "event risks" and add and average them together for a patent's total risk score.
 
        "risk_label": "Medium", 	# we can fine tune these labels + their thresholds. 
        "source": "synthetic_event"	# can def remove this
    }
```

# Things to add:
Time to complete, compared to total time given for the event.
If someone was doing their work really fast, they might not be doing a good job.
TC 1600: 19hrs average
TC 1700: 13.4hrs average
TC 2100: 18.1hrs average
TC 2400 17.55586hrs average
TC 2600: 20.6hrs average
TC 2800: 15.1497hrs average
TC 3600: 12.18382hrs average
TC 3700: 12.0hrs average
Overall Timeline length : (event history)
First action to final decision

# TODO:

- Create better mock data. Make more "reviewers".
- Need to get a hold of patent claims so I can derive both: a) a corpus for similarity scores, b) a way to analyze claim complexity. (if we go forward with this idea)
- [SBERT Classification]([url](https://github.com/AI-Growth-Lab/PatentSBERTa)) - Implementing this for patent classification, labelling, to bin for possible future sim searching
- [Bert Classificiation] (https://github.com/jiehsheng/PatentBERT) - The prequel to SBERT, probably also for patent classification. 
- [Kaggle Patent identification] https://www.kaggle.com/competitions/us-patent-phrase-to-phrase-matching - Kaggle one
- [Semantic Similarity] https://github.com/zzy99/My-competition-solutions
- https://hpi.de/naumann/projects/web-science/paar-patent-analysis-and-retrieval/patentmatch.html#:~:text=PatentMatch%3A%C2%A0A%20Dataset%20for%20Matching%20Patent,Claims%20%26%20Prior%20Art
- https://www.gaipalliance.org/pqai#:~:text=Solution
- https://hkashima.github.io/publication/IAMOT2010.pdf#:~:text=In%20this%20paper%2C%20we%20extend,Next%2C%20extending%20the
- https://github.com/mahesh-maan/awesome-patent-retrieval
- https://www.kaggle.com/c/uspto-explainable-ai
