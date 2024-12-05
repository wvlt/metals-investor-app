from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key for session security

# Load company data from the new CSV
company_data = pd.read_csv('manual_company_data.csv')

# Drop rows where company_name is NaN
company_data = company_data.dropna(subset=['company_name'])

# Replace NaN values with None
company_data = company_data.where(pd.notnull(company_data), None)

# Load lithium price data from CSV
lithium_data = pd.read_csv('lithium_historical_prices.csv')

@app.route('/')
def index():
    # Create Plotly figure with two traces
    fig = go.Figure()

    # Add LITHIUM trace
    fig.add_trace(go.Scatter(x=lithium_data['date'], y=lithium_data['price'], mode='lines', name='price', line=dict(color='red', width=4)))

    # Update layout
    fig.update_layout(title='Lithium Prices Over Time', xaxis_title='Date', yaxis_title='Price (USD)')

    # Convert Plotly figure to HTML
    graph_html = pio.to_html(fig, full_html=False)
    
    # Get the latest price and date
    latest_data = lithium_data.iloc[-1]
    latest_price = f"{latest_data['price']:.1f}"
    latest_date = latest_data['date']
    
    return render_template('index.html', graph_html=graph_html, latest_price=latest_price, latest_date=latest_date)


@app.route('/valuation', methods=['GET', 'POST'])
def valuation():
    company_info = None
    if request.method == 'POST':
        query = request.form.get('company_name', '').lower()
        company_info = company_data[company_data['company_name'].str.lower().str.contains(query, na=False)].to_dict(orient='records')
    else:
        # Load the first row of the CSV by default
        company_info = company_data.iloc[:1].to_dict(orient='records')
    
    # Replace None values with 'Data not available'
    for info in company_info:
        for key, value in info.items():
            if value is None:
                info[key] = 'Data not available'

    return render_template('valuation.html', company_info=company_info)

@app.route('/comparison', methods=['GET'])
def comparison():
    search_term = request.args.get('search', '').strip()
    
    if 'previous_search_results' not in session:
        session['previous_search_results'] = []
    
    previous_search_results = session['previous_search_results']

    if search_term:
        filtered_df = company_data[company_data['company_name'].str.contains(search_term, case=False, na=False)]
        search_results = filtered_df.to_dict(orient='records')
        for result in search_results:
            if not any(company['company_name'] == result['company_name'] for company in previous_search_results):
                previous_search_results.append(result)
        session['previous_search_results'] = previous_search_results

    columns = [
        'company_name', 'market_cap_m_dollar', 'last_price', '52_week_high_low', 
        'volume', 'float_%', 'inst._ownership_%', 'div._yield_%'
    ]
    df = pd.DataFrame(previous_search_results, columns=columns)
    df.columns = ['company_name', 'market_cap_m_dollar', 'last_price', '52_week_high_low', 
                  'volume', 'float_', 'inst_ownership_', 'div_yield_']

    companies = df.to_dict(orient='records')  # No limit on companies
    return render_template('comparison.html', companies=companies)

@app.route('/screening')
def screening():
    columns = [
        'company_name', 'last_price', 'NYSE', 'last_delayed', 'VWAP_delayed', 'open', 
        'previous_close', 'day_high_low', '52_week_high_low', 'beta_3y', 
        'market_cap_m_dollar', 'p/ltm_eps_(x)_ranked', 'p/ntm_eps_(x)_ranked', 
        'price/book_(x)_ranked', 'price/tang_book_(x)_ranked', 'tev/ltm_total_revenue_(x)_ranked', 
        'tev/ltm_ebitda_(x)_ranked', 'total_debt/ebitda_(x)_ranked', 'average_Rank'
    ]
    companies = company_data[columns].to_dict(orient='records')
    return render_template('screening.html', companies=companies)


@app.route('/search_company')
def search_company():
    query = request.args.get('query', '').lower()
    result = company_data[company_data['company_name'].str.lower().str.contains(query, na=False)].to_dict(orient='records')
    return jsonify(result[:3])  # Limit to a maximum of 3 results

@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        suggestions = company_data[company_data['company_name'].str.lower().str.contains(query, na=False)]['company_name'].head(10).tolist()
    return jsonify(suggestions)

@app.route('/remove_company', methods=['POST'])
def remove_company():
    company_name = request.json.get('company_name')
    if 'previous_search_results' in session:
        session['previous_search_results'] = [
            company for company in session['previous_search_results'] 
            if company['company_name'] != company_name
        ]
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7862)
