import json
import os
import sys
import numpy as np
import yfinance as yf
import mplfinance as mpf
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from sklearn.linear_model import LinearRegression
from AIFiles.NivFuncs import Niamh
class ShortTermTraderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.niv = Niamh

        self.setWindowTitle('Short-Term Price Predictor')
        self.setGeometry(100, 100, 800, 600)

        # Set up the layout
        layout = QVBoxLayout(self)

        # Add a canvas and a toolbar for mplfinance
        self.canvas = FigureCanvas(mpf.figure(style='charles', figsize=(10, 6)))
        layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        # Add combo boxes for selecting symbol, chart type, and refresh rate
        self.symbol_selector = QComboBox(self)
        self.symbol_selector.addItems(['TSLA', 'AAPL', 'GC=F', 'MCD', 'EURUSD=X', 'EURGBP=X'])
        self.symbol_selector.currentIndexChanged.connect(self.on_symbol_changed)
        layout.addWidget(self.symbol_selector)

        self.chart_type_selector = QComboBox(self)
        self.chart_type_selector.addItems(['candle', 'Linear Regresion Prediction'])
        self.chart_type_selector.currentIndexChanged.connect(self.on_chart_type_changed)
        layout.addWidget(self.chart_type_selector)

        self.refresh_rate_selector = QComboBox(self)
        self.refresh_rate_selector.addItems(['5 seconds', '10 seconds', '30 seconds', '1 minute', '5 minutes'])
        self.refresh_rate_selector.currentIndexChanged.connect(self.on_refresh_rate_changed)
        layout.addWidget(self.refresh_rate_selector)

        # Add the analysis button
        self.analysis_button = QPushButton('Perform Analysis', self)
        self.analysis_button.clicked.connect(self.perform_analysis)
        layout.addWidget(self.analysis_button)

        # Initialize the refresh rate (default to 30 seconds)
        self.refresh_rate_seconds = 30

        # Set up a timer to refresh the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_plot)
        self.timer.start(self.refresh_rate_seconds * 1000)  # Start with the default refresh rate

        # Initialize the stock symbol or currency pair
        self.symbol = self.symbol_selector.currentText()

        # Initialize the chart type
        self.chart_type = self.chart_type_selector.currentText()

        # Number of future points to predict
        self.prediction_points = 30

        self.refresh_plot()  # Initial call to refresh the plot

    def on_refresh_rate_changed(self, index):
        refresh_rates = [5, 10, 30, 60, 300]
        self.refresh_rate_seconds = refresh_rates[index]

        # Update the timer interval based on the selected refresh rate
        self.timer.setInterval(self.refresh_rate_seconds * 1000)

    def on_symbol_changed(self, index):
        self.symbol = self.symbol_selector.itemText(index)
        self.refresh_plot()

    def on_chart_type_changed(self, index):
        self.chart_type = self.chart_type_selector.itemText(index)
        self.refresh_plot()

    def fetch_stock_data(self, ticker):
        data = yf.download(ticker, period='3d', interval='1m')
        savedata = yf.download(ticker, period='1mo', interval='5m')
        # Create a folder for the stock if it doesn't exist
        stock_folder = os.path.join("Stocks", ticker)
        if not os.path.exists(stock_folder):
            os.makedirs(stock_folder)
        txt_file_path = f"{ticker}_data.txt"

        # Save the data to a text file
        with open("Stocks/"+ticker+"/"+txt_file_path, 'w') as txt_file:
            txt_file.write(savedata.to_string())

        print(f"Data saved to {txt_file_path}")
        chart_image_path = os.path.join(stock_folder, f"{ticker}_chart.png")
        try:
            last_2_hours_data = savedata.iloc[-120:]  # Select the last 2 hours of data
            self.plot_stock_data(last_2_hours_data)  # Plot the last 2 hours of data before saving the image
            self.canvas.figure.savefig(chart_image_path, bbox_inches='tight', format='png', dpi=300)
            print(f"Chart image saved to {chart_image_path}")
        except Exception as e:
            print(f"Error saving chart image: {e}")

        # Save data to a JSON file with the ticker name for the past 10 years
        json_file_path = os.path.join(stock_folder, f"{ticker}_data.json")
        try:
            data_copy = savedata.copy()  # Create a copy to avoid modifying the original DataFrame
            data_copy.index = data_copy.index.strftime('%Y-%m-%dT%H:%M:%S')  # Convert index to string format

            # Convert DataFrame to a list of dictionaries with datetime included
            data_list = data_copy.reset_index().to_dict(orient='records')

            with open(json_file_path, 'w') as json_file:
                for record in data_list:
                    json_file.write(f"{json.dumps(record)}\n")
            print(f"JSON data saved to {json_file_path}")
        except Exception as e:
            print(f"Error saving JSON data: {e}")

        return data

    def plot_stock_data(self, data):
        # Clear the previous figure
        self.canvas.figure.clear()

        # Create an axis
        ax = self.canvas.figure.add_subplot(111)

        # Plot according to the selected chart type
        if self.chart_type == 'candle':
            mpf.plot(data, ax=ax, type='candle', style='charles', datetime_format='%H:%M', warn_too_much_data=1000)
            current_price = data['Close'].iloc[-1]
            ax.axhline(y=current_price, color='r', linestyle='-', linewidth=2, label='Current Price')
            self.canvas.figure.text(1.02, current_price, f'{current_price:.2f}',
                                    verticalalignment='center', horizontalalignment='left',
                                    transform=ax.get_yaxis_transform(),
                                    color='r', fontsize=10)
        elif self.chart_type == 'Linear Regresion Prediction':
            mpf.plot(data, ax=ax, type='line', style='charles', datetime_format='%H:%M', warn_too_much_data=1000)
            current_price = data['Close'].iloc[-1]
            ax.axhline(y=current_price, color='r', linestyle='-', linewidth=2, label='Current Price')
            self.canvas.figure.text(1.02, current_price, f'{current_price:.2f}',
                                    verticalalignment='center', horizontalalignment='left',
                                    transform=ax.get_yaxis_transform(),
                                    color='r', fontsize=10)
            future_x, future_y, future_y2, future_y3, triangle_x = self.predict_next_prices(data)

            # Plot the predicted data
            ax.plot(future_x.flatten(), future_y, color='orange', linestyle='--', label='Predicted')

            # Connect the triangle to the end of the original prediction line
            ax.plot([future_x[-1], triangle_x[0]], [future_y[-1], future_y2[0]], color='gray', linestyle='--', alpha=0.5)
            ax.plot([future_x[-1], triangle_x[0]], [future_y[-1], future_y3[0]], color='gray', linestyle='--', alpha=0.5)

            # Plot the triangle-like figure
            ax.plot(triangle_x.flatten(), future_y2, color='green', linestyle='--', label='Predicted (Upper)')
            ax.plot(triangle_x.flatten(), future_y3, color='red', linestyle='--', label='Predicted (Lower)')

        ax.legend()
        self.canvas.draw()

    def refresh_plot(self):
        new_data = self.fetch_stock_data(self.symbol)
        self.plot_stock_data(new_data)


    def perform_analysis(self):
        pass
        #QMessageBox.information(self, 'Analysis Opinion', opinion)

    def predict_next_prices(self, data):
        x = np.arange(len(data.index)).reshape(-1, 1)
        y = data['Close'].values
        model = LinearRegression().fit(x, y)

        future_x = np.arange(len(data.index), len(data.index) + self.prediction_points).reshape(-1, 1)
        future_y = model.predict(future_x)

        # Predict three additional prices forming a triangle
        triangle_length = self.prediction_points  # You can adjust the length of the triangle
        triangle_x = np.linspace(future_x[-1], future_x[-1] + triangle_length, num=triangle_length).reshape(-1, 1)
        future_y2 = future_y * 1.02  # You can adjust the multiplier as needed
        future_y3 = future_y * 0.98  # You can adjust the multiplier as needed

        return future_x, future_y, future_y2, future_y3, triangle_x

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShortTermTraderApp()
    ex.show()
    sys.exit(app.exec_())
