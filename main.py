#%% Imports
from common_imports import pd, np, tk, ttk, messagebox, sco, plt, FigureCanvasTkAgg, yf, Figure, sm, go, sns, datetime, timedelta
from data_functions import fetch_data, plot_data, calculate_statistic

# Global variable to store the current dataframe
current_data = None
#%% Enter Ticker
def analyze_ticker():
    global current_data
    ticker = ticker_entry.get().upper()  # Get the ticker symbol from the entry widget, make it uppercase
    start = start_date_entry.get()
    end = end_date_entry.get()
    current_data, message = fetch_data(ticker, start, end)  # Fetch the data for the entered ticker and date range
    update_message(message)
    if current_data is not None:
        column_selector['values'] = current_data.columns.tolist() 

def update_message(text):
    message_label.config(text=text)  # Update the text of the message_label to show the current status

def reset_all():
    # Clear global data
    global current_data
    current_data = None

    # Reset labels and text fields
    volume_correlation_label.config(text="")
    top_days_label.config(text="")
    high_vol_label.config(text="")
    low_vol_label.config(text="")
    message_label.config(text="")

    stat_result.set("")  # Assuming there's a StringVar for results
    if 'column_selector' in globals():  # Check if dropdown is initialized
        column_selector.set('')  # Reset dropdown

    # Clear plots
    for widget in volume_plot_frame.winfo_children():
        widget.destroy()
    for widget in volatility_plot_frame.winfo_children():
        widget.destroy()

    # Optionally clear any text entries or other widgets
    ticker_entry.delete(0, 'end')
    # Additional widgets to clear can be added here

#%% Exploratory Data Analysis

def handle_stat_click(stat_func):
    column = column_selector.get()
    result = calculate_statistic(current_data, column, stat_func)
    stat_result.set(result)

def handle_plot_click():
    column = column_selector.get()
    if current_data is not None and column:
        plot_data(tab_exploratory, column, current_data)  # Pass the parent frame and column to plot
    else:
        update_message("Select a column and fetch data before plotting.")

def update_columns_dropdown(df):
    column_selector['values'] = list(df.columns)
    column_selector.current(0)

# Function to load data
def load_data(filepath):
    return pd.read_csv(filepath)

# Function to calculate descriptive statistics
def descriptive_stats(data, column):
    desc_stats = data[column].describe()
    return desc_stats

# Function to plot closing prices over time
def plot_closing_prices(data):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], data['Close'], label='Closing Price')
    plt.title('Closing Prices Over Time')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.legend()
    plt.show()

#%% Volatility Analysis

# Function to calculate daily percentage change
def calculate_daily_changes(data):
    if data is not None and 'Close' in data.columns:
        data['Daily Change (%)'] = data['Close'].pct_change() * 100
        return data[['Close', 'Daily Change (%)']], "Calculation successful"
    else:
        return None, "Data not available or 'Close' column missing"
    
def get_top_volatility_days(data):
    if data is not None and 'Daily Change (%)' in data.columns:
        # Include the index (date) as a regular column for display
        data['Date'] = data.index
        top_days = data[['Date', 'Close', 'Daily Change (%)']].nlargest(5, 'Daily Change (%)', 'all')
        return top_days, "Top volatility days calculated"
    else:
        return None, "Data not available or 'Daily Change (%)' column missing"
    
def handle_volatility_analysis():
    changes, message = calculate_daily_changes(current_data)
    if changes is not None:
        plot_volatility(changes)
        top_volatility_days, vol_message = get_top_volatility_days(changes)
        display_top_volatility_days(top_volatility_days)
    update_message(message)

def display_top_volatility_days(data):
    # Update text display to include date
    top_days_label.config(text=f"Top 5 Volatility Days:\n{data.to_string(index=False)}")

def plot_volatility(data):
    fig = plt.Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(111)
    plot.hist(data['Daily Change (%)'].dropna(), bins=30, color='blue', alpha=0.7)
    plot.set_title('Histogram of Daily Percentage Changes')
    plot.set_xlabel('Daily Change (%)')
    plot.set_ylabel('Frequency')

    canvas = FigureCanvasTkAgg(fig, master=volatility_plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

#%% Volume Analysis
# Function to analyze volume and daily percentage change
def calculate_volume_correlation(data):
    if data is not None and 'Volume' in data.columns and 'Daily Change (%)' in data.columns:
        correlation = data['Volume'].corr(data['Daily Change (%)'])
        return correlation, "Correlation calculation successful"
    else:
        return None, "Data not available or necessary columns missing"

def prepare_volume_data(data):
    if data is not None and 'Volume' in data.columns:
        return data['Volume'], "Volume data prepared"
    else:
        return None, "Data not available or 'Volume' column missing"
    
def get_volume_extremes(data):
    if data is not None and 'Volume' in data.columns:
        highest_volume = data.nlargest(5, 'Volume')[['Volume']]  # Top 5 days of highest volume
        lowest_volume = data.nsmallest(5, 'Volume')[['Volume']]  # Top 5 days of lowest volume
        return highest_volume, lowest_volume, "Volume extremes calculated."
    else:
        return None, None, "Data not available or 'Volume' column missing."

def handle_volume_analysis():
    correlation, message = calculate_volume_correlation(current_data)
    update_message(message)
    if correlation is not None:
        volume_correlation_label.config(text=f"Volume to Daily Change Correlation: {correlation:.2f}")

    volume_data, vol_message = prepare_volume_data(current_data)
    update_message(vol_message)
    if volume_data is not None:
        plot_volume(volume_data)

    # Get and display volume extremes
    high_vol, low_vol, vol_ext_message = get_volume_extremes(current_data)
    if high_vol is not None and low_vol is not None:
        display_volume_extremes(high_vol, low_vol)
    else:
        update_message(vol_ext_message)

def display_volume_extremes(high_vol, low_vol):
        high_vol_label.config(text=f"Highest Volume Days:\n{high_vol.to_string()}")
        low_vol_label.config(text=f"Lowest Volume Days:\n{low_vol.to_string()}")


def plot_volume(data):
    fig = plt.Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(111)
    plot.bar(data.index, data, color='purple', alpha=0.7)
    plot.set_title('Trading Volume Over Time')
    plot.set_xlabel('Date')
    plot.set_ylabel('Volume')

    canvas = FigureCanvasTkAgg(fig, master=volume_plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

global plot_frame

# Main window
root = tk.Tk()
root.title("Financial Data Analysis Tool")

# Creating the main frame for the notebook
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create the notebook
notebook = ttk.Notebook(main_frame)
notebook.pack(fill='both', expand=True)

#%% Tab 1: Ticker Input
tab_ticker = ttk.Frame(notebook)
notebook.add(tab_ticker, text="Ticker Input")

# Widgets for Ticker Input
ticker_label = ttk.Label(tab_ticker, text="Enter Ticker:")
ticker_label.grid(column=0, row=0, sticky=tk.W, pady=2)

ticker_entry = ttk.Entry(tab_ticker)
ticker_entry.grid(column=1, row=0, sticky=tk.W, pady=2)

# Date range entries
date_label = ttk.Label(tab_ticker, text="Enter Date Range (optional, YYYY-MM-DD):")
date_label.grid(column=0, row=1, sticky=tk.W, pady=2)

start_date_label = ttk.Label(tab_ticker, text="Start Date:")
start_date_label.grid(column=0, row=2, sticky=tk.W, pady=2)
start_date_entry = ttk.Entry(tab_ticker, width=20)
start_date_entry.grid(column=1, row=2, pady=2)

end_date_label = ttk.Label(tab_ticker, text="End Date:")
end_date_label.grid(column=0, row=3, sticky=tk.W, pady=2)
end_date_entry = ttk.Entry(tab_ticker, width=20)
end_date_entry.grid(column=1, row=3, pady=2)

ticker_button = ttk.Button(tab_ticker, text="Fetch Data", command=lambda: analyze_ticker())
ticker_button.grid(column=2, row=0)
reset_button = ttk.Button(tab_ticker, text="Reset All", command=reset_all)
reset_button.grid(row=5, column=0, sticky=tk.W, pady=2)



# Status message label
message_label = ttk.Label(tab_ticker)
message_label.grid(column=0, row=4, columnspan=3)


#%% Tab 2: Exploratory Data Analysis

tab_exploratory = ttk.Frame(notebook)
notebook.add(tab_exploratory, text="Exploratory Data Analysis")

# Widgets for Exploratory Data Analysis
column_label = ttk.Label(tab_exploratory, text="Select Column:")
column_label.grid(row=0, column=0)
column_selector = ttk.Combobox(tab_exploratory, width=15, state="readonly")
column_selector.grid(row=0, column=1)
plot_button = ttk.Button(tab_exploratory, text="Plot", command=lambda: handle_plot_click())
plot_button.grid(row=0, column=2)
stat_result = tk.StringVar()
result_label = ttk.Label(tab_exploratory, textvariable=stat_result)
result_label.grid(row=2, column=0, columnspan=3)
 # Subframe for plots
plot_frame = ttk.Frame(tab_exploratory)
plot_frame.grid(row=4, column=0, columnspan=6, pady=(10, 0), sticky="nsew")


# Statistic buttons
stats = {"Mean": pd.Series.mean, "Median": pd.Series.median, "Std Dev": pd.Series.std, "Min": pd.Series.min, "Max": pd.Series.max}
column_idx = 0
for stat_name, stat_func in stats.items():
    btn = ttk.Button(tab_exploratory, text=stat_name, command=lambda f=stat_func: handle_stat_click(f))
    btn.grid(row=1, column=column_idx)
    column_idx += 1

#%% Tab 3: Volatility Analysis
tab_volatility = ttk.Frame(notebook, padding="10")
notebook.add(tab_volatility, text="Volatility Analysis")

# Volatility Analysis Widgets
volatility_button = ttk.Button(tab_volatility, text="Analyze Volatility", command=handle_volatility_analysis)
volatility_button.pack(side="top", fill="x")
volatility_plot_frame = ttk.Frame(tab_volatility)
volatility_plot_frame.pack(side="top", fill="both", expand=True)

# Label to display top volatility days
top_days_label = tk.Label(tab_volatility, justify=tk.LEFT, anchor="w", font=('Courier', 10))
top_days_label.pack(side="top", fill="both", expand=True)

#%% Tab 4: Volume Analysis
# Volume Analysis Tab setup
tab_volume = ttk.Frame(notebook)
notebook.add(tab_volume, text="Volume Analysis")

volume_button = ttk.Button(tab_volume, text="Analyze Volume", command=handle_volume_analysis)
volume_button.pack(side="top", fill="x")

volume_plot_frame = ttk.Frame(tab_volume)
volume_plot_frame.pack(side="top", fill="both", expand=True)

volume_correlation_label = ttk.Label(tab_volume)
volume_correlation_label.pack(side="top", fill="x")

# Grid configuration for side-by-side display of volume extremes
extreme_frame = ttk.Frame(tab_volume)
extreme_frame.pack(side="top", fill="x", expand=True)

high_vol_label = ttk.Label(extreme_frame, justify=tk.LEFT, anchor="n")
high_vol_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

low_vol_label = ttk.Label(extreme_frame, justify=tk.LEFT, anchor="n")
low_vol_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
# Start the GUI event loop
root.mainloop()