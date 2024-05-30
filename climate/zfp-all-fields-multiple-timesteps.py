import xarray as xr
import numpy as np

from tqdm import tqdm
from ANL_utilities import *

# Disable file lock
os.environ['VISUS_DISABLE_WRITE_LOCK'] = '1'

local_nc_files = ['NASA/2016/cstm_d01_2016-05-01_00_00_00.nc', 'NASA/2016/cstm_d01_2016-05-01_01_00_03.nc']
local_idx_file = 'zfp-all-fields-multiple-timesteps.idx'

fields = get_fields()
dims = get_dims(reverse=True)

print(f'Creating idx file {local_idx_file} ...')
idx_file = CreateIdx(url=local_idx_file, dims=dims, fields=fields,
                     time=[0, len(local_nc_files) - 1, '%06d/'], compression='raw')

for i, file_name in enumerate(local_nc_files):
    print(f'Opening netcdf file {file_name} ...')
    nc_file = xr.open_dataset(file_name)

    print(f'Writing fields ...')
    for field in tqdm(fields):
        data = np.squeeze(nc_file[field.name].values)

        idx_file.write(data=data, time=i, field=field.name)

start = time.time()
print(f'Compressing idx file ...')
idx_file.compressDataset(['zfp-16-16'])
print(f'Compression finished {(time.time() - start):.02f}s')

