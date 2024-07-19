from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Path to the CSV file
csv_file_path = '/Users/dangtho/Python Project/thpt/diem_thi_thpt_2024_modified.csv'

@app.route('/get_scores')
def get_scores():
    province = request.args.get('province')
    subject = request.args.get('subject')
    
    if not province or not subject:
        return jsonify({"error": "Missing province or subject parameter"}), 400

    try:
        # Read the CSV file with 'sbd' as string
        df = pd.read_csv(csv_file_path, dtype={'sbd': str})
        
        # Extract the province code from sbd
        df['province_code'] = df['sbd'].str[:2]

        # Filter data based on province code
        filtered_df = df[df['province_code'] == province].copy()  # Make a copy of the filtered DataFrame

        # Replace empty values and 'none' with -1
        if subject in filtered_df.columns:
            filtered_df[subject] = filtered_df[subject].replace({'none': -1, '': -1}).astype(float)
        else:
            return jsonify({"error": f"Subject '{subject}' not found in the data"}), 400

        # Include -1 in the scores list
        scores = filtered_df[subject].tolist()
        
        # Define histogram bins based on subject
        if subject in ['toan', 'ngoai_ngu']:
            bins = np.arange(-1, 10.4, 0.2)  # Ensure 10.2 to include 10 in bins
        else:
            bins = np.arange(-1, 10.5, 0.25)  # Ensure 10.25 to include 10 in bins

        # Calculate histogram
        counts, bin_edges = np.histogram(scores, bins=bins)

        # Format bin edges to avoid floating-point precision issues
        bin_edges = np.round(bin_edges, decimals=2).tolist()
        counts = counts.tolist()

        result = {
            "scores": bin_edges[:-1],  # Exclude the last bin edge for scores
            "counts": counts
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
