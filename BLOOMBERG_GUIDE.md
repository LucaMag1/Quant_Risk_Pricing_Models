
# Bloomberg Global Trading Challenge

## Data Requirements

This strategy uses historical daily equity prices exported from Bloomberg. The original dataset is not included due to licensing restrictions.

## How to Run

1. Obtain your own historical daily equity price dataset.
2. Create a `data` folder alongside the Python script.
3. Save your dataset as `prices.csv` inside that folder.
4. Ensure the CSV contains a date column followed by one column per stock containing historical closing prices.
5. Install the required Python libraries:
   ```bash
   pip install pandas numpy matplotlib
   ```
6. Run `Bloomberg_Global_Trading_Challenge.py`.

## Output

The script generates **`momentum_top20.csv`**, containing the ranked stock candidates.

## Limitations

The rankings are based on historical data and do not guarantee future investment performance. Results depend on the dataset and period analysed.
