
### Thermal Monitoring Network Data
Data Science in Practice Fall 2023
Project Sponsor: https://healthycities.sice.indiana.edu/
![Screenshot 2023-12-23 190616](https://github.com/MustafaAlsaegh/Thermal_Monitoring_Network_Dashboard/assets/96810312/601a36aa-c4f5-4a71-88a8-6c490e8ac915)
#### Overview

This repository contains code and data for monitoring and analyzing Bloomington heat sensor data. We have developed an interactive dashboard using Flask+Plotly to visualize and analyze the collected data. The backend fetches relevant data based on user requests, and the frontend utilizes Plotly to create interactive visualizations.

#### Approach

1. **Data Collection:**
   - Temperature, Relative Humidity, and Moisture data are collected from sensors placed in various locations in Bloomington, including:
     - Biology Building
     - Dunn Woods
     - Dunn Meadow
     - Campus River
     - Woodlawn
     - Wells Library Parking Lot
     - Myles Brand Parking Lot
     - Fee Lane
     - Merrill Hall
   - National Weather Service (NWS) data set for Monroe County is obtained from the sensor at Monroe County Airport.

2. **Data Processing:**
   - Outliers in the dataset are detected and handled.
   - Heat index values are computed for predicting heat waves.

3. **Visualization:**
   - An interactive time series line graph is created to illustrate selected weather parameters over time.
   - Spatial visualizations show the distribution of weather parameters across sensor locations.
   - Boxplots are used to explain the variance of weather parameters.

#### Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/ThermalMonitoringNetwork_Data.git
    cd ThermalMonitoringNetwork_Data
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask application:

    ```bash
    python app.py
    ```

4. Open your browser and navigate to [http://localhost:5000](http://localhost:5000) to access the interactive dashboard.

#### Data Details

- **Sensor Locations:**
  - Biology Building
  - Dunn Woods
  - Dunn Meadow
  - Campus River
  - Woodlawn
  - Wells Library Parking Lot
  - Myles Brand Parking Lot
  - Fee Lane
  - Merrill Hall

- **Additional Data:**
  - National Weather Service (NWS) data set for Monroe County from Monroe County Airport sensor.

#### Visualizations

The initial demonstration for sponsors includes:
- Visualizations with tick marks on the preview chart, addressing the requirement not provided by Plotly JS by default.

#### Contributors

- [Your Name]
- [Collaborator 1]
- [Collaborator 2]

Feel free to contribute to the project by forking the repository and submitting pull requests. If you have any questions or issues, please open an [issue](https://github.com/your-username/ThermalMonitoringNetwork_Data/issues).

**Thank you for your interest in Thermal Monitoring Network Data!**
