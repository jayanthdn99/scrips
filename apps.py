import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import requests
import json
from datetime import datetime, timedelta

# Initialize the Dash app
app = dash.Dash(__name__, title="Stock Visualization Dashboard")
server = app.server  # Needed for Render deployment

# Function to get stock data from Alpha Vantage API (free tier)
def get_stock_data(symbol, days=90):
    # Using Alpha Vantage's free API (limited to 25 calls per day)
    # You should replace this with your own API key
    api_key = "demo"  # Replace with your Alpha Vantage API key
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format for API
    function = "TIME_SERIES_DAILY"
    output_size = "full"
    
    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&outputsize={output_size}"
    
    # Demo data in case API calls are exhausted
    demo_data = {
        "AAPL": [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)],
        "MSFT": [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)],
        "values": {
            "AAPL": [150 + i * 0.5 + (i % 5) for i in range(days)],
            "MSFT": [250 + i * 0.3 + (i % 7) for i in range(days)]
        }
    }
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            dates = []
            values = []
            
            for date, values_dict in data["Time Series (Daily)"].items():
                if datetime.strptime(date, "%Y-%m-%d") >= start_date:
                    dates.append(date)
                    values.append(float(values_dict["4. close"]))
            
            # Sort by date
            dates_values = sorted(zip(dates, values), key=lambda x: x[0])
            dates = [d for d, v in dates_values]
            values = [v for d, v in dates_values]
            
            return dates, values
        else:
            # Use demo data if API call fails
            return demo_data[symbol], demo_data["values"][symbol]
    except:
        # Use demo data if API call fails
        return demo_data[symbol], demo_data["values"][symbol]

# Define the layout
app.layout = html.Div([
    html.H1("Stock Price Visualization Dashboard", style={"textAlign": "center"}),
    
    html.Div([
        html.Div([
            html.H3("Select stocks to compare:"),
            dcc.Dropdown(
                id='stock-selector',
                options=[
                    {'label': 'Apple (AAPL)', 'value': 'AAPL'},
                    {'label': 'Microsoft (MSFT)', 'value': 'MSFT'}
                ],
                value=['AAPL'],  # Default selections
                multi=True
            ),
            
            html.H3("Select time period:"),
            dcc.RadioItems(
                id='time-period',
                options=[
                    {'label': '1 Month', 'value': 30},
                    {'label': '3 Months', 'value': 90},
                    {'label': '6 Months', 'value': 180}
                ],
                value=90,
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            dcc.Graph(id='stock-graph')
        ], style={'width': '70%', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        html.H3("Note about API Usage"),
        html.P("This app uses Alpha Vantage's free API which is limited to 25 calls per day. If the API limit is reached, demo data will be displayed.")
    ], style={'margin-top': '20px'})
])

@callback(
    Output('stock-graph', 'figure'),
    [Input('stock-selector', 'value'),
     Input('time-period', 'value')]
)
def update_graph(selected_stocks, days):
    if not selected_stocks:
        # Return empty figure
        return px.line()
    
    # Get data for each stock
    all_data = []
    for stock in selected_stocks:
        dates, values = get_stock_data(stock, days)
        for date, value in zip(dates, values):
            all_data.append({
                'Date': date,
                'Price': value,
                'Stock': stock
            })
    
    # Create figure
    fig = px.line(all_data, x='Date', y='Price', color='Stock',
                 title=f"Stock Prices Over Last {days} Days")
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
