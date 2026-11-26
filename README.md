# IndiePulse

A Streamlit exploratory dashboard built from the Steam Games Dataset 2025 (snapshot described as January 2025).

## Run locally

1. Install Python 3.10+.
2. In this folder, run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Dataset

`games.csv` contains a processed catalog with game metadata and genre labels. `review_summary.csv` contains aggregated counts and positive-review share for the review rows supplied in the dataset. The original archive contained a large reviews file; it was summarized during preprocessing to make the app easier to run.

## Caveats

The dataset is a snapshot, not live data. Genre labels are multilingual, so the indie filter is heuristic and imperfect. Review aggregates are only as representative as the included rows. The gross estimate (sample reviews × USD price × 35) is illustrative and not actual revenue. Opportunity score is a transparent experimental heuristic, not a validated prediction.
