from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

data = pd.read_csv('manual_company_data.csv')

data_info = data[['company_name', 'ceo', 'cfo_and_vp_finance', 'NYSE', 'company_description', 'headquarters', 'status', 'topic_tags', 'date_of_incorporation', 'web_address']]
financial_data = data[['company_name', 'last_price', 'market_cap_m_dollar', 
                       'total_revenue_$000_2022', 'total_revenue_$000_2023', 'total_revenue_$000_2024', 
                       'total_assets_$000_2022', 'total_assets_$000_2023', 'total_assets_$000_2024', 
                       'total_liabilities_$000_2022', 'total_liabilities_$000_2023', 'total_liabilities_$000_2024', 
                       'total_equity_$000_2022', 'total_equity_$000_2023', 'total_equity_$000_2024', 
                       'cash_&_short_term_investments_$000_2022', 'cash_&_short_term_investments_$000_2023', 
                       'cash_&_short_term_investments_$000_2024', 'net_debt_$000_2022', 
                       'net_debt_$000_2023', 'net_debt_$000_2024']]
valuation_data = data[['company_name', 'EBITDA_$000_2022', 'EBITDA_$000_2023', 'EBITDA_$000_2024', 
                       'EBIT_$000_2022', 'EBIT_$000_2023', 'EBIT_$000_2024', 
                       'net_income_$000_2022', 'net_income_$000_2023', 'net_income_$000_2024', 
                       'book_value_per_share_$_2022', 'book_value_per_share_$_2023', 'book_value_per_share_$_2024', 
                       'enterprisevalue=debt+equity_cash', ' EV/EBITDA', 'latest_book_value_per_share_$_', 
                       'latest_EBITDA']]

@app.route('/', methods=['GET', 'POST'])
def index():
    company_info = None
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        company_info = data_info[data_info['company_name'].str.contains(company_name, case=False, na=False)]
    return render_template('index.html', company_info=company_info)

@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('query', '')
    if query:
        suggestions = data_info[data_info['company_name'].str.contains(query, case=False, na=False)]['company_name'].head(10).tolist()
    else:
        suggestions = []
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7864)
