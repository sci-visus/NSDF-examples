import requests
import xarray as xr
from tqdm import tqdm
from NEX_GDDP_CMIP6_utilities import *

# Define CMIP6 dataset variables
years = {'start': 1950, 'end': 1950}  # TODO: Change end year back to 2100
scenario = 'historical'
model = 'ACCESS-CM2'
variant = 'r1i1p1f1'
version = ''  # Other versions: v1.1, v1.2
variables = ['tas']

# Variables to hold the latitude and longitude extents and steps
# TODO: grab these from the dataset's netcdf files
longitude = {'min': 0.125, 'max': 359.875, 'step': 0.25}
latitude = {'min': -59.875, 'max': 89.875, 'step': 0.25}
num_rows = 1440
num_cols = 600

# File specific variables
base_url = 'https://nex-gddp-cmip6.s3-us-west-2.amazonaws.com/NEX-GDDP-CMIP6/'
local_root_dir = f'./NEX-GDDP-CMIP6_data/'
local_nc_dir = f'{local_root_dir}data/'
local_idx_dir = f'{local_root_dir}idx/'

# Check if directories exist and create them if not
create_directory(local_root_dir)
create_directory(local_nc_dir)
create_directory(local_idx_dir)

# Create an IDX field for each variable of the dataset
idx_fields = []
for variable in variables:
    field = Field(variable, 'float32')
    idx_fields.append(field)

# Create an IDX file
idx_file_name = build_file_name(model, '', scenario, variant, version, 0, 'idx')
idx_file = CreateIdx(url=local_idx_dir + idx_file_name, fields=idx_fields,
                     dims=[num_rows, num_cols], time=[years['start'] * 365, ((years['end'] + 1) * 365) - 1, f'%08d/'])
print(f'Created IDX file: {idx_file_name}')

# Go through each field/variable
for variable in variables:
    first = True
    min_value = 0
    max_value = 0
    start_time = time.time()
    end_time = start_time

    for year in range(years['start'], years['end'] + 1):

        # Netcdf file specific variables
        nc_file_name = build_file_name(model, variable, scenario, variant, '', year, 'nc')
        url = build_url(base_url, model, variable, scenario, variant)
        local_file_name = local_nc_dir + nc_file_name

        # Check if file exists and if not, download and write it
        if os.path.exists(local_file_name):
            print(f'Local NetCDF file exists: {local_file_name}')
        else:
            print(f'Local NetCDF file not found: {nc_file_name}')
            print(f'Downloading NetCDF file from: {url + nc_file_name}')

            response = requests.get(url + nc_file_name, allow_redirects=True)
            open(local_file_name, 'wb').write(response.content)

            print(f'Local NetCDF file created: {local_file_name}')

        # Load dataset from the local file
        print(f'Loading {variable} data...')
        dataset = xr.open_dataset(local_file_name)
        data = dataset[variable].values

        # TODO: Set the min / max of each field

        print(f'Writing data..')
        # Write each day's data into the idx file
        for day in tqdm(range(365)):
            time_step = get_timestep(year, day)
            day_data = data[day]

            idx_file.write(data=day_data, field=variable, time=time_step)
            idx_file.compressDataset(['zip'], timestep=time_step)

        # Cleanup
        dataset.close()
        os.remove(local_file_name)  # Remove used NetCDF file to save storage

        # Get elapsed time between each year
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time

        print(f'Variable: {variable}, Year: {year}, Elapsed Time: {elapsed_time}s')
