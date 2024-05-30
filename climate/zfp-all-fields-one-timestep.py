import xarray as xr
import numpy as np

from tqdm import tqdm
from ANL_utilities import *

# Disable file lock
os.environ['VISUS_DISABLE_WRITE_LOCK'] = '1'

local_nc_file = 'NASA/2016/cstm_d01_2016-05-01_00_00_00.nc'
local_idx_file = 'zfp-all-fields-one-timestep.idx'

fields = get_fields()
dims = get_dims(reverse=True)

print(f'Creating idx file {local_idx_file} ...')
idx_file = CreateIdx(url=local_idx_file, dims=dims, fields=fields,
                     time=[0, 0, '%06d/'], compression='raw')

print(f'Opening netcdf file {local_nc_file} ...')
nc_file = xr.open_dataset(local_nc_file)

print(f'Writing fields ...')
for field in tqdm(fields):
    data = np.squeeze(nc_file[field.name].values)

    idx_file.write(data=data, time=0, field=field.name)

start = time.time()
print(f'Compressing idx file ...')
idx_file.compressDataset(['zfp-16-16'])
print(f'Compression finished {(time.time() - start):.02f}s')

