import xarray as xr
import numpy as np

from ANL_utilities import *

# Disable file lock
os.environ['VISUS_DISABLE_WRITE_LOCK'] = '1'

local_nc_file = 'NASA/2016/cstm_d01_2016-05-01_00_00_00.nc'
local_idx_file = 'zfp-one-field.idx'
field = 'precipitation_0m'

dims = get_dims(reverse=True)

print(f'Creating idx file {local_idx_file} ...')
idx_file = CreateIdx(url=local_idx_file, dims=dims, fields=[Field(field, 'float32')],
                     time=[0, 0, '%06d/'], compression='raw')

print(f'Opening netcdf file {local_nc_file} ...')
nc_file = xr.open_dataset(local_nc_file)
data = np.squeeze(nc_file[field].values)

print(f'Writing field {field} ...')
idx_file.write(data=data, time=0, field=field)

start = time.time()
print(f'Compressing idx file ...')
idx_file.compressDataset(['zfp-16-16'])
print(f'Compression finished {(time.time() - start):.02f}s')
