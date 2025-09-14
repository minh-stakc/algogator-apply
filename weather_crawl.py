import cdsapi
url="https://cds.climate.copernicus.eu/api"
key="123456789abcdefghj"
c = cdsapi.Client(url, key)

c.retrieve(
    'reanalysis-era5-land',
    {
        'variable': ['2m_temperature', 'total_precipitation'],
        'area': [49, -104, 36, -89],  #  (Corn Belt location)
        'format': 'netcdf',
        'year': [str(y) for y in range(2020, 2026)],
        'month': [f"{m:02d}" for m in range(1, 13)], 
        'day': "all",
        'time': ['00:00'],
    },
    'data_0.nc'
)
