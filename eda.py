import pandas as pd
import plotly.express as px
df= pd.read_csv("smart_home_iot_dataset.csv")

print(df.shape)
print(df.info())

missing = df.isnull().sum()

print("missing values: ",missing[missing > 0])
## some columns had missing data which was less than 5% of total data

print("duplicates: ",df.duplicated().sum(),"\n")
## no duplicates found

columns = [
    "battery_level_pct",
    "temperature_c",
    "humidity_pct",
    "co2_ppm",
    "voc_ppb",
    "light_lux",
    "pm25_ugm3",
    "rssi_dbm",
    "latency_ms"
]

for col in columns:
    df[col] = df[col].fillna(df[col].median())
## replaced all null columns with median values

missing = df.isnull().sum()

print("missing values: ",missing[missing > 0],"\n")

print("datatypes: ", df.dtypes,"\n")

print("describe: ",df.describe())
print("min time: ",df["timestamp"].min(),"\n")
print("max time: ",df["timestamp"].max(),"\n")
print("rooms: ",df["room"].nunique(),"\n")

print("devices: ",df["device_type"].nunique(),"\n")

print("manufacturers: ",df["manufacturer"].nunique(),"\n")

print("average power consumption of each room:",df.groupby("room")["power_consumption_w"].mean(),"\n")

print("average temprature of room:",df.groupby("room")["temperature_c"].mean(),"\n")

print("average latency of devices: ",df.groupby("device_type")["latency_ms"].mean(),"\n")

print("no.of failures that can occur in 7 days: ",df["failure_within_7days"].value_counts())

print("box plot of temperature: ")

fig1=px.box(df, y="temperature_c",title="Temperature Distribution")
fig1.show()

print(df["anomaly_label"].value_counts())
print(df[df["temperature_c"] > 50].shape)

print(df[df["temperature_c"] < 0].shape)
print(df[df["temperature_c"] > 50]["anomaly_label"].value_counts())

# Temperature contains outliers beyond the IQR boundaries (7.7°C to 33.49°C), Median is 20.63°C. Box plot analysis identified temperature values below 0°C and above 50°C as outliers according to the IQR method. Since these observations constitute less than 1% of the dataset and may represent unusual environmental conditions or sensor behavior, they were retained for analysis rather than removed.

print("box plot of power consumption: ")
fig2=px.box(df, y="power_consumption_w", title="Power Distribution")
fig2.show() 

device = (
    df["device_type"]
      .value_counts()
      .reset_index()
)

device.columns = ["device_type", "count"]

fig = px.pie(
    device,
    names="device_type",
    values="count",
    title="Device Type Distribution"
)

fig.show()

# save cleaned dataset
df.to_csv("smart_home_iot_dataset_cleaned.csv", index=False)