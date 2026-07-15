from dash import html, Dash, dcc,Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import numpy as np

# df = pd.read_csv("smart_home_iot_dataset_cleaned.csv")

engine = create_engine(
    "mysql+pymysql://dashboard:Nishtha123@localhost/SENSORS"
)

print("Table uploaded successfully!")

query = """
SELECT *
FROM smart_home_iot_dataset_cleaned;
"""

df = pd.read_sql(query, engine)

column_names = {
    "temperature_c": "Temperature (°C)",
    "humidity_pct": "Humidity (%)",
    "co2_ppm": "CO₂ (ppm)",
    "voc_ppb": "VOC (ppb)",
    "pm25_ugm3": "PM2.5 (µg/m³)",
    "power_consumption_w": "Power Consumption (W)",
    "voltage_v": "Voltage (V)",
    "current_a": "Current (A)",
    "battery_level_pct": "Battery Level (%)",
    "latency_ms": "Network Latency (ms)",
    "energy_kwh_daily": "Daily Energy (kWh)",
    "device_type": "Device Type",
    "manufacturer": "Manufacturer",
    "protocol": "Protocol",
    "room": "Room"
}

device_names = {
    "smart_plug": "Smart Plug",
    "smoke_detector": "Smoke Detector",
    "motion_sensor": "Motion Sensor",
    "air_purifier": "Air Purifier",
    "smart_light": "Smart Light",
    "security_camera": "Security Camera",
    "thermostat": "Thermostat",
    "door_lock": "Smart Door Lock",
    "water_leak_sensor": "Water Leak Sensor",
    "window_sensor": "Window Sensor",
    "CO2_sensor": "CO₂ Sensor",
    "energy_monitor": "Energy Monitor",
    "ip_camera": "IP Camera",
    "door_sensor": "Door Sensor",
    "humidity_sensor": "Humidity Sensor"
    
}

print("hey ",df["failure_within_7days"].dtype)
print(df["device_type"].unique())

print(len(df))
df["timestamp"] = pd.to_datetime(df["timestamp"]) ## timestamp was object converted to datetime
start_date=df['timestamp'].min().date()
end_date=df['timestamp'].max().date()

missing = df.isnull().sum()

print("missing values: ",missing[missing > 0])

app=Dash(__name__) 

app.layout= html.Div([ 
html.H1("Smart Home IOT Analytics Dashboard",className='heading'), 
html.Div([ 
html.P('Select Category', className='selection'),
 html.P('Select Date range', className='range'), 
],className='selectors'), 
html.Div([ 
dcc.Dropdown( 
id='dropdown', 
className='dropdown', 
options=[ 
{'label':'Correlation between sensor measurements','value':'Readings'}, 
{'label':'Temprature line chart','value':'temperature'}, 
{'label':'Average hourly power consumeption across room','value':'power_consumed'},
{'label':'Network Latency Over Time','value':'latency'},
{'label': 'Network Latency Heatmap (Protocol × Manufacturer)','value':'latency_heatmap'},
{'label': 'Failure Prediction by Device Type','value': 'failure_device'},
{'label': 'energy per device','value': 'energy_device'}

], 
value='Readings' 
), 
dcc.DatePickerRange(
id="date",
min_date_allowed=start_date,
max_date_allowed=end_date,
start_date=start_date,
end_date=end_date
)
 ], className='tools'),

  html.Div([

        html.Div([
            dcc.Graph(
                id="main-graph",
                responsive=True,
                style={"height": "75vh"}
            )
        ], className="graph-container"),

        html.Div(
            id="summary-box",
            className="summary-container"
        )

    ], className="dashboard-row")

])
@app.callback(
    Output('main-graph', 'figure'),
    Output("summary-box","children"),
    Input('dropdown', 'value'),
    Input('date','start_date'),
    Input('date','end_date')
)
def update_graphs(selected,start_date, end_date):

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + pd.Timedelta(days=1)

    filtered_df = df[
    (df["timestamp"] >= start) &
    (df["timestamp"] < end)
    ].copy()


    if filtered_df.empty:
        fig = px.scatter(title="No data selected for date range")

        summary = html.Div([
        html.H3("Summary"),
        html.P("No data available for the selected date range.")
    ])

        return fig, summary
    if selected=='Readings':
        columns = [
            "temperature_c",
            "humidity_pct",
            "co2_ppm",
            "voc_ppb",
            "pm25_ugm3",
            "power_consumption_w",
            "voltage_v",
            "current_a",
            "battery_level_pct"
        ]

        filtered_df["humidity_pct"] = pd.to_numeric(
        filtered_df["humidity_pct"],
        errors="coerce"
        )

        corr = filtered_df[columns].corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Correlation Between Sensor Measurements"
        )

        fig.update_layout(
            height=700,
            width=900
            )
        
        upper = corr.where(
            np.triu(np.ones(corr.shape), k=1).astype(bool)
        )

    # Strongest positive correlation
        positive_pair = upper.stack().idxmax()
        positive_value = upper.stack().max()

    # Strongest negative correlation
        negative_pair = upper.stack().idxmin()
        negative_value = upper.stack().min()

    #average absolute correlation
        avg_corr = upper.abs().stack().mean()

    #insight
        if avg_corr < 0.2:
            insight = "Most sensor measurements are weakly correlated, indicating that sensors capture different aspects of the environment."

        elif avg_corr < 0.5:
            insight = "Most sensor measurements show weak to moderate relationships."

        else:
            insight = "Several sensor measurements exhibit strong relationships."
        
        summary = html.Div([

            html.H3("📊 Correlation Summary", className="summary-title"),

            html.Div([
            html.H4("📈 Highest Positive"),
            html.P(f"{column_names[positive_pair[0]]} ↔ {column_names[positive_pair[1]]}"),
            html.H3(f"{positive_value:.2f}")
        ], className="summary-card positive"),

        html.Div([
        html.H4("📉 Highest Negative"),
        html.P(f"{column_names[negative_pair[0]]} ↔ {column_names[negative_pair[1]]}"),
        html.H3(f"{negative_value:.2f}")
        ], className="summary-card negative"),

        html.Div([
        html.H4("⭐ Average Correlation"),
        html.H3(f"{avg_corr:.2f}")
        ], className="summary-card average"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(insight)
        ], className="summary-card insight")

        ], className="summary-container")

        return fig, summary

    elif selected == 'power_consumed':
        filtered_df = filtered_df.copy()
        filtered_df["hour"] = filtered_df["timestamp"].dt.hour

        pivot = filtered_df.pivot_table(
            values="power_consumption_w",
            index="room",
            columns="hour",
            aggfunc="mean"
        )

        fig = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn_r",
            aspect="auto",
            title="Average Power Consumption by Room and Hour"
        )

        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Room"
        )

        fig.update_traces(
        hovertemplate=
        "<b>%{y}</b><br>" +
        "Hour: %{x}:00<br>" +
        "Average Power: %{z:.2f} W<extra></extra>"
        )

        #Overall average power consumption
        avg_power = pivot.mean().mean()

        # Highest and lowest values directly from the heatmap
        highest_room, highest_hour = pivot.stack().idxmax()
        highest_room_power = pivot.stack().max()

        lowest_room, lowest_hour = pivot.stack().idxmin()
        lowest_room_power = pivot.stack().min()

    #average power by hour
        hour_avg = (
            filtered_df
            .groupby("hour")["power_consumption_w"]
            .mean()
        )

        peak_hour = hour_avg.idxmax()
        peak_power = hour_avg.max()

        # observation
        if peak_power > avg_power * 1.2:
            observation = (
            f"Power usage peaks around {peak_hour}:00, "
            "indicating significantly higher energy demand during this hour."
        )
        else:
            observation = (
            "Power consumption remains fairly consistent throughout the day."
        )
            
        summary = html.Div([

        html.H3("Power Consumption Summary"),

        html.P([
            html.B("Overall Average Power: "),
            f"{avg_power:.2f} W"
        ]),

        html.P([
            html.B("Highest Consuming Room: "),
            f"{highest_room} at {highest_hour}:00 ({highest_room_power:.2f} W)"
        ]),

        html.P([
            html.B("Lowest Consuming Room: "),
            f"{lowest_room} at {lowest_hour}:00 ({lowest_room_power:.2f} W)"
        ]),

        html.P([
            html.B("Peak Usage Hour: "),
            f"{peak_hour}:00 ({peak_power:.2f} W)"
        ]),

        html.P([
            html.B("Observation: "),
            observation
        ])

    ])

        return fig,summary

    elif selected == "temperature":

        temp_df = (
            filtered_df
            .assign(Date=filtered_df["timestamp"].dt.date)
            .groupby("Date")["temperature_c"]
            .mean()
            .reset_index()
        )

        avg_temp = temp_df["temperature_c"].mean()
        max_temp = temp_df["temperature_c"].max()
        min_temp = temp_df["temperature_c"].min()

        #date of highest average temperature
        hottest_row = temp_df.loc[temp_df["temperature_c"].idxmax()]

        hottest_day = hottest_row["Date"]
        highest_temp = hottest_row["temperature_c"]

        #Temperature range
        temp_range = max_temp - min_temp

        #Observation
        if temp_range < 5:
            observation = "Temperature remained fairly stable throughout the selected period."
        elif temp_range < 10:
            observation = "Temperature showed moderate variation over the selected period."
        else:
            observation = "Temperature fluctuated significantly during the selected period."

        fig = px.line(
        temp_df,
        x="Date",
        y="temperature_c",
        title="Average Temperature Over Time",
        markers=True
        )

        fig.update_layout(
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Average Temperature (°C)"
        )

        summary = html.Div([

        html.H3("🌡️ Temperature Summary", className="summary-title"),

        html.Div([
        html.H4("🌡️ Average Temperature"),
        html.H3(f"{avg_temp:.1f} °C")
        ], className="summary-card average"),

        html.Div([
        html.H4("🔥 Highest Average"),
        html.H3(f"{max_temp:.1f} °C")
        ], className="summary-card negative"),

        html.Div([
        html.H4("❄️ Lowest Average"),
        html.H3(f"{min_temp:.1f} °C")
        ], className="summary-card positive"),

        html.Div([
        html.H4("☀️ Warmest Day"),
        html.P(hottest_day),
        html.H3(f"{highest_temp:.1f} °C")
        ], className="summary-card peak"),

        html.Div([
        html.H4("📏 Temperature Range"),
        html.H3(f"{temp_range:.1f} °C")
        ], className="summary-card average"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(observation)
        ], className="summary-card insight")

    ], className="summary-container")

        return fig,summary
    
    elif selected == 'latency':

        latency_df = (
            filtered_df
            .assign(Date=filtered_df["timestamp"].dt.date)
            .groupby("Date")["latency_ms"]
            .mean()
            .reset_index()
        )


        fig = px.line(
            latency_df,
            x="Date",
            y="latency_ms",
            title="Average Network Latency Over Time",
                 markers=True
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Average Latency (ms)",
            title_x=0.5
        )

        avg_latency = latency_df["latency_ms"].mean()
        max_latency = latency_df["latency_ms"].max()
        min_latency = latency_df["latency_ms"].min()

        highest_latency_day = latency_df.loc[
            latency_df["latency_ms"].idxmax(),
            "Date"
        ]

        latency_range = max_latency - min_latency

        #observation
        if latency_range < 20:
            observation = "Network latency remained stable throughout the selected period."

        elif latency_range < 50:
            observation = "Network latency showed moderate fluctuations."

        else:
            observation = "Network latency fluctuated significantly during the selected period."

        summary = html.Div([

            html.H3("🌐 Network Latency Summary", className="summary-title"),

        html.Div([
        html.H4("📊 Average Latency"),
        html.H3(f"{avg_latency:.2f} ms")
        ], className="summary-card average"),

        html.Div([
        html.H4("🔴 Highest Latency"),
        html.H3(f"{max_latency:.2f} ms")
        ], className="summary-card negative"),

        html.Div([
        html.H4("🟢 Lowest Latency"),
        html.H3(f"{min_latency:.2f} ms")
        ], className="summary-card positive"),

        html.Div([
        html.H4("📅 Highest Latency Day"),
        html.P(str(highest_latency_day))
        ], className="summary-card peak"),

        html.Div([
        html.H4("📏 Latency Range"),
        html.H3(f"{latency_range:.2f} ms")
        ], className="summary-card average"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(observation)
        ], className="summary-card insight")

    ], className="summary-container")

        return fig,summary 
    
    elif selected == 'energy_device':

        energy_df = (
        filtered_df
        .groupby("device_type")["energy_kwh_daily"]
        .mean()
        .reset_index()
        )

        energy_df = energy_df.sort_values(
            by="energy_kwh_daily",
            ascending=False
        )

        avg_energy = energy_df["energy_kwh_daily"].mean()

        highest_device = energy_df.iloc[0]["device_type"]
        highest_energy = energy_df.iloc[0]["energy_kwh_daily"]

        lowest_device = energy_df.iloc[-1]["device_type"]
        lowest_energy = energy_df.iloc[-1]["energy_kwh_daily"]

        energy_diff = highest_energy - lowest_energy

        #observation
        if energy_diff < 2:
            observation = "Energy consumption is fairly uniform across device types."
        elif energy_diff < 5:
            observation = "Some device types consume noticeably more energy than others."
        else:
            observation = "There is a significant variation in energy consumption between device types."

        energy_df["Device"] = energy_df["device_type"].map(device_names)

        fig = px.bar(
            energy_df,
            x="Device",
            y="energy_kwh_daily",
            color="energy_kwh_daily",
            title="Average Daily Energy Consumption by Device Type",
            labels={
                "device_type": "Device Type",
                "energy_kwh_daily": "Average Energy (kWh)"
            },
            text_auto=".2f"
        )

        fig.update_layout(
            title_x=0.5,
            xaxis_title="Device Type",
            yaxis_title="Average Daily Energy (kWh)",
            xaxis_tickangle=-30
        )

        summary = html.Div([

        html.H3("⚡ Energy Consumption Summary", className="summary-title"),

        html.Div([
        html.H4("⚡ Average Energy"),
        html.H3(f"{avg_energy:.2f} kWh/day")
        ], className="summary-card average"),

        html.Div([
        html.H4("🔋 Highest Consumer"),
        html.P(device_names.get(highest_device, highest_device)),
        html.H3(f"{highest_energy:.2f} kWh/day")
        ], className="summary-card negative"),

        html.Div([
        html.H4("🌿 Lowest Consumer"),
        html.P(device_names.get(lowest_device, lowest_device)),
        html.H3(f"{lowest_energy:.2f} kWh/day")
        ], className="summary-card positive"),

        html.Div([
        html.H4("📊 Consumption Difference"),
        html.H3(f"{energy_diff:.2f} kWh/day")
            ], className="summary-card peak"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(observation)
        ], className="summary-card insight")

    ], className="summary-container")
        return fig,summary

    elif selected == "latency_heatmap":

        pivot = filtered_df.pivot_table(
        values="latency_ms",
        index="protocol",
        columns="manufacturer",
        aggfunc="mean"
    )

        #Overall average latency
        avg_latency = pivot.mean().mean()

        # Fastest and slowest cells in the heatmap
        fastest_protocol, fastest_manufacturer = pivot.stack().idxmin()
        fastest_latency = pivot.stack().min()

        slowest_protocol, slowest_manufacturer = pivot.stack().idxmax()
        slowest_latency = pivot.stack().max()

        #highest latency combo
        highest_cell = pivot.stack().idxmax()
        highest_latency = pivot.stack().max()

        #lowest latency combo
        lowest_cell = pivot.stack().idxmin()
        lowest_latency = pivot.stack().min()

        #Observation
        if highest_latency - lowest_latency < 20:
            observation = "Network latency is fairly consistent across protocols and manufacturers."
        elif highest_latency - lowest_latency < 50:
            observation = "Moderate latency differences exist between protocol-manufacturer combinations."
        else:
            observation = "Certain protocol-manufacturer combinations experience considerably higher latency."

        fig = px.imshow(
        pivot,
        color_continuous_scale="Plasma",
        text_auto=".1f",
        aspect="auto",
        title="Average Network Latency by Protocol and Manufacturer"
        )

        fig.update_layout(
        title_x=0.5,
        xaxis_title="Manufacturer",
        yaxis_title="Protocol",
        coloraxis_colorbar_title="Latency (ms)"
        )

        summary = html.Div([

        html.H3("🌐 Latency Heatmap Summary", className="summary-title"),

        html.Div([
        html.H4("📊 Average Latency"),
        html.H3(f"{avg_latency:.2f} ms")
        ], className="summary-card average"),

        html.Div([
        html.H4("🚀 Fastest Connection"),
        html.P(f"{fastest_protocol} + {fastest_manufacturer}"),
        html.H3(f"{fastest_latency:.2f} ms")
        ], className="summary-card positive"),

        html.Div([
        html.H4("🐢 Slowest Connection"),
        html.P(f"{slowest_protocol} + {slowest_manufacturer}"),
        html.H3(f"{slowest_latency:.2f} ms")
        ], className="summary-card negative"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(observation)
        ], className="summary-card insight")

        ], className="summary-container")

        return fig, summary

    elif selected == "failure_device":

        failure_df = (
            filtered_df[filtered_df["failure_within_7days"] == 1]
            .groupby("device_type")
            .size()
            .reset_index(name="Failure Count")
            .sort_values(by="Failure Count", ascending=False)
        )

        if failure_df.empty:
            fig = px.bar(title="No predicted failures found for the selected date range")

            summary = html.Div([
                html.H3("Failure Prediction Summary"),
                html.P("No failures were predicted for the selected date range.")
            ])

            return fig, summary

        #Total predicted failures
        total_failures = failure_df["Failure Count"].sum()

        #Number of device types affected
        affected_devices = len(failure_df)

        #Device with highest and lowest failures
        highest_device = failure_df.iloc[0]["device_type"]
        lowest_device = failure_df.iloc[-1]["device_type"]
        highest_device = device_names.get(highest_device, highest_device)
        highest_count = failure_df.iloc[0]["Failure Count"]
        
        lowest_device = device_names.get(lowest_device, lowest_device)
        lowest_count = failure_df.iloc[-1]["Failure Count"]

        if highest_count <= 5:
            observation = "Very few predicted failures were observed across all device types."
        elif highest_count <= 20:
            observation = "A moderate number of predicted failures are concentrated in a few device types."
        else:
            observation = "One or more device types show a high number of predicted failures and may require attention."

        fig = px.bar(
        failure_df,
        x="device_type",
        y="Failure Count",
        color="Failure Count",
        text="Failure Count",
        color_continuous_scale="Reds",
        title="Predicted Device Failures Within the Next 7 Days"
        )

        fig.update_layout(
        title_x=0.5,
        xaxis_title="Device Type",
        yaxis_title="Number of Predicted Failures",
        xaxis_tickangle=-30
        )

        if failure_df.empty:
            fig = px.bar(title="No predicted failures found for the selected date range")

        summary = html.Div([

        html.H3("⚠️ Failure Prediction Summary", className="summary-title"),

        html.Div([
        html.H4("📊 Total Predicted Failures"),
        html.H3(str(total_failures))
        ], className="summary-card average"),

        html.Div([
        html.H4("🖥️ Affected Device Types"),
        html.H3(str(affected_devices))
        ], className="summary-card peak"),

        html.Div([
        html.H4("🔴 Most Predicted Failures"),
        html.P(highest_device),
        html.H3(f"{highest_count} Devices")
        ], className="summary-card negative"),

        html.Div([
        html.H4("🟢 Least Predicted Failures"),
        html.P(lowest_device),
        html.H3(f"{lowest_count} Devices")
        ], className="summary-card positive"),

        html.Div([
        html.H4("💡 Key Insight"),
        html.P(observation)
        ], className="summary-card insight")

    ], className="summary-container")

        fig.update_traces(textposition="outside")

        return fig, summary

    else:
        fig = px.scatter(title="Select a graph")
        summary = html.Div()

    fig.update_layout(
        title_x=0.5,
        template='plotly_white',
        height=600,
        yaxis_tickformat=".2s"

    )
    fig.update_xaxes(side='bottom')
    
    print("done")

    return fig,summary

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=False)