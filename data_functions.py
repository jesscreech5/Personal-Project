#%% Imports
from common_imports import pd, np, tk, ttk, messagebox, sco, plt, FigureCanvasTkAgg, yf, Figure, sm, go, sns, datetime, timedelta

def fetch_data(ticker, start, end):
    if not start or not end:
        end = datetime.now()
        start = end - timedelta(days=365)
        end, start = end.strftime('%Y-%m-%d'), start.strftime('%Y-%m-%d')
        
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)
        long_name = stock.info.get('longName', ticker)
        print(df.columns)
        if df.empty:
            return None, f"No data found for {long_name}."
        else:
            return df, f"Data for {long_name} fetched successfully."
    except Exception as e:
        return None, f"Error: {str(e)}"

def plot_data(master, column, data):
    

    if data is not None and column in data.columns:

        fig = Figure(figsize=(5, 4), dpi=100)
        plot = fig.add_subplot(111)
        plot.plot(data.index, data[column].dropna())
        plot.set_title(f'Plot of {column}')
        plot.set_xlabel('Date')
        plot.set_ylabel(column)

        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=4, column=0, columnspan=6, pady=(10,0))
        
    else:
        fig = None
        return "No data available or column invalid."
        

def calculate_statistic(data, column, function):
    if data is not None and column in data.columns:
        try:
            result = function(data[column].dropna())
            return f"{column} {function.__name__}: {result:.2f}"
        except Exception as e:
            return f"Error calculating {function.__name__}: {str(e)}"
    else:
        return "No data available or column invalid."