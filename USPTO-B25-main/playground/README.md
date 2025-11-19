# Playground

Current Toys: Similarity Score Generation.

``generate_claim_sim_score.py``: takes in a csv file, ``patent_claims_fulltext.csv``, found in the USPTO open database. 

`generate_claim_bins`: generates bins for similarity score matching, based on the domain keywords, provided within `domain_mapping.txt`. This is a very simple match based on keywords only, but it works for a very simple case. This generates `patent_claims_with_domains.csv`

`generate_claim_sim_score_with_binning`:takes in the csv file `patent_claims_with_domains.csv`, which is structured the same as `patent_claims_fulltext.csv`, but contains an extra column, `domain`. This acts as a bin when we do our similarity searching. 

Both scripts:
1) Parses the rows to get patent id, claim number, and claim text.
2) generates a similarity measure (in schema below), based on cosine similarity. 
3) links the patent claims to the same patent, and gather's the top 3 similar patent claims (that are not present in it's patent membership)

```
e.g. Patent A : Claim 1 will NOT get similarity scores for Patent A: Claim 2.
```

The schema is shown below:
```
{
  "3930271": [ # this is the patent ID, parsed from the table
    {
      "claim_number": 1,
      "top_3_similar": [
        {
          "patent_number": 3930334,
          "claim_number": 11,
          "sim_score": 0.3514249147118335
        },
        {
          "patent_number": 3930334,
          "claim_number": 1,
          "sim_score": 0.33671326615518815
        },
        {
          "patent_number": 3930334,
          "claim_number": 10,
          "sim_score": 0.3165419416631157
        }
      ]
    },
    {
      "claim_number": 4,
      "top_3_similar": [
        {
          "patent_number": 3930273,
          "claim_number": 10,
          "sim_score": 0.2351888909668297
        },
        {
          "patent_number": 3930273,
          "claim_number": 12,
          "sim_score": 0.23493997955130685
        },
        {
          "patent_number": 3930273,
          "claim_number": 14,
          "sim_score": 0.2344779617505609
        }
      ]
    },
    {
      "claim_number": 3,
      "top_3_similar": [
        {
          "patent_number": 3930273,
          "claim_number": 10,
          "sim_score": 0.31638709238104296
        },
        {
          "patent_number": 3930273,
          "claim_number": 12,
          "sim_score": 0.3160522451070328
        },
        {
          "patent_number": 3930273,
          "claim_number": 14,
          "sim_score": 0.3154307171598352
        }
      ]
    },
    {
      "claim_number": 2,
      "top_3_similar": [
        {
          "patent_number": 3930334,
          "claim_number": 11,
          "sim_score": 0.33639641623116695
        },
        {
          "patent_number": 3930334,
          "claim_number": 5,
          "sim_score": 0.3332064249793062
        },
        {
          "patent_number": 3930334,
          "claim_number": 1,
          "sim_score": 0.31279055024520586
        }
      ]
    }
  ],
}
```
