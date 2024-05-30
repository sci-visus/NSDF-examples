import xarray as xr
import numpy as np

from ANL_utilities import *

os.environ["VISUS_DISABLE_WRITE_LOCK"] = "1"


def main(compression, nc_dir, idx_dir, idx_file_template, file_name):
    try:
        start_time = time.time()

        fields = get_fields()

        # Load data
        nc_file = xr.open_dataset(nc_dir + file_name)
        time_step = convert_date_to_time_step(nc_file['times'].values[0].decode('utf-8'))

        # Create IDX
        idx_file = CreateIdx(url=idx_dir + f'timestep_{time_step}.idx', dims=get_dims(reverse=True),
                             fields=fields, time=[time_step, time_step, f'%06d/'],
                             filename_template=idx_file_template, compression='raw')

        for field in fields:
            data = np.squeeze(nc_file[field.name].values)
            idx_file.write(data=data, field=field.name, time=time_step)

        idx_file.compressDataset([compression], timestep=time_step)

        print(f'Finished {file_name} in {(time.time() - start_time):.04f} seconds')

        os.remove(idx_dir + f'timestep_{time_step}.idx')

        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
