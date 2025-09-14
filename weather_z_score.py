import xarray as xr

ds = xr.open_dataset("data_0.nc", engine="netcdf4", chunks={"time": 100})

print(ds)

corn_belt = ds.sel(latitude=slice(45, 35), longitude=slice(-100, -85))
wheat_belt = ds.sel(latitude=slice(48, 35), longitude=slice(-105, -95))

corn_daily = corn_belt.resample(valid_time="1D").mean()
corn_daily["tp"] = corn_belt["tp"].resample(valid_time="1D").sum()

wheat_daily = wheat_belt.resample(valid_time="1D").mean()
wheat_daily["tp"] = wheat_belt["tp"].resample(valid_time="1D").sum()

# print(corn_daily["t2m"].mean(dim=("latitude","longitude")).to_dataframe().head(20))
# print(corn_daily["tp"].mean(dim=("latitude","longitude")).to_dataframe().head(20))

def compute_zscore_xr(da, window=30):
    regional_mean = da.mean(dim=("latitude", "longitude"))
    rolling_mean = regional_mean.rolling(valid_time=window, center=True, min_periods=5).mean()
    rolling_std = regional_mean.rolling(valid_time=window, center=True, min_periods=5).std()
    return (regional_mean - rolling_mean) / rolling_std

corn_temp_z = compute_zscore_xr(corn_daily["t2m"])
corn_precip_z = compute_zscore_xr(corn_daily["tp"])

wheat_temp_z = compute_zscore_xr(wheat_daily["t2m"])
wheat_precip_z = compute_zscore_xr(wheat_daily["tp"])

corn_temp_df = corn_temp_z.to_dataframe().reset_index().drop(columns=["number"])
corn_precip_df = corn_precip_z.to_dataframe().reset_index().drop(columns=["number"])
wheat_temp_df = wheat_temp_z.to_dataframe().reset_index().drop(columns=["number"])
wheat_precip_df = wheat_precip_z.to_dataframe().reset_index().drop(columns=["number"])

weather_df = (
    corn_temp_df.rename(columns={"t2m": "corn_temp_z", "valid_time": "Date"})
    .merge(corn_precip_df.rename(columns={"tp": "corn_precip_z", "valid_time": "Date"}), on="Date")
    .merge(wheat_temp_df.rename(columns={"t2m": "wheat_temp_z", "valid_time": "Date"}), on="Date")
    .merge(wheat_precip_df.rename(columns={"tp": "wheat_precip_z", "valid_time": "Date"}), on="Date")
)


weather_df.to_csv("weather_sentiment.csv", index=False)
