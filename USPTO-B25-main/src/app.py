from flask import Flask, send_from_directory

app = Flask(__name__)

# Route for the main dashboard (serves HTML)
@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

# Route to serve data.json
@app.route('/data.json')
def get_data():
    return send_from_directory('.', 'patent_events.json')


@app.route('/risk-summary')
def risk_dash():
    return send_from_directory('.', 'risk_summary.html')


@app.route('/risk-summary-data')
def risk_summary():
    # Return the JSON directly (no template needed)
    return send_from_directory('.', 'model_summary_high_risk.json')


if __name__ == '__main__':
    app.run(debug=True)

