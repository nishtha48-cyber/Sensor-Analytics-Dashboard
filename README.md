# Sensor-Analytics-Dashboard
## 🏠 Home IoT Sensor Analytics Dashboard

An interactive analytics dashboard developed using Python, Dash, Plotly, Pandas, SQLAlchemy, and MySQL to monitor and analyze smart home IoT sensor data. The dashboard enables users to explore environmental conditions, device performance, energy consumption, network health, and predictive maintenance through interactive visualizations and dynamic summaries.

## Features
- 📊 Correlation heatmap between environmental and electrical sensor measurements
- 🌡️ Temperature trend analysis with dynamic date filtering
- ⚡ Hourly power consumption heatmap across different rooms
- 📶 Network latency trend visualization
- 🌐 Protocol vs Manufacturer latency heatmap
- 🔋 Energy consumption comparison across device types
- ⚠️ Failure prediction analysis for IoT devices
- 📅 Interactive date range filtering
- 📝 Automatically generated summaries and key insights for every visualization
- 💾 MySQL database integration using SQLAlchemy
- 🔌 REST APIs for fetching sensor and dashboard data
- 📈 Interactive Plotly visualizations with hover information

## Tech Stack
- Python
- Dash
- Plotly Express
- FastAPI
- Pandas
- NumPy
- SQLAlchemy
- MySQL
- HTML & CSS

## 🔌 API Endpoints


| Endpoint | Description |
|----------|-------------|
| `GET /sensors` | Retrieve the first 50 sensor readings from the dataset. |
| `GET /devices` | Fetch all unique IoT devices along with room, manufacturer, model, and device type. |
| `GET /maintenance?limit=100&offset=0` | Retrieve devices that are due for maintenance with pagination support. |
| `GET /room_stats` | Get average temperature, humidity, and power consumption for each room. |
| `GET /failure_risk` | Fetch devices predicted to fail within the next 7 days. |
| `GET /low_battery` | Retrieve devices with battery level below 20%. |
| `GET /avg_battery_manufacturer` | Get the average battery level grouped by manufacturer. |

### POST Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /new_reading` | Insert a new IoT sensor reading into the database. |
| `POST /security` | Log a security event into the security logs table. |

## Data Processing
- Missing value treatment using median imputation
- Duplicate detection
- Outlier analysis
- Exploratory Data Analysis (EDA)
- Dynamic filtering and aggregation
- Dashboard Highlights
- Responsive dashboard layout
- Dynamic KPI summaries
- Clean and intuitive user interface
- Multiple visualization types including line charts, heatmaps, bar charts, and correlation matrices
