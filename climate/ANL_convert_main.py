import multiprocessing
import subprocess
import sys
import xarray as xr

from ANL_utilities import *

python_exe = 'python3'
time_step_script = 'ANL_convert_timestep.py'

year = 2016
compression = 'zfp-16-16'
nc_directory = f'NASA/{year}/'
idx_directory = 'ANL-data-idx/'
idx_file_name = f'ANL-data-{year}-{compression}.idx'
idx_file_name_template = f'./ANL-data-{year}-{compression}/%04x.bin'

failed_files = []


def run_time_step(file_name):
    result = subprocess.run([python_exe, time_step_script, compression, nc_directory, idx_directory, idx_file_name_template, file_name])

    if result.returncode != 0:
        print(f'Failed to convert file: {file_name}')
        failed_files.append(file_name)


def main(start_index: int = 0, end_index: int | None = None):
    all_files = list_files(nc_directory)
    files = all_files[start_index:] if end_index is None else all_files[start_index:end_index]

    create_directory(idx_directory)

    # Get the first timestep of the first file
    first_nc_file = xr.open_dataset(nc_directory + all_files[0])
    starting_time_step = convert_date_to_time_step(first_nc_file['times'].values[0].decode('utf-8'))

    # Create the main IDX file
    idx_file = CreateIdx(url=idx_directory + idx_file_name, fields=get_fields(), dims=get_dims(True),
                         time=[starting_time_step, starting_time_step + len(all_files) - 1, '%06d/'], compression='raw')

    # Used to set the default_compression parameter of each field
    print(f'Setting each field\'s default compression to {compression}')
    idx_file.compressDataset([compression])

    print(f'Beginning conversion of {len(files)} files')
    with multiprocessing.Pool(math.floor(os.cpu_count() / 2)) as pool:
        try:
            pool.map(run_time_step, files)
        except Exception as e:
            print(f'Error: {e}')

    print(f'Failed to convert {len(failed_files)} files')

    for file in failed_files:
        print(f'{file}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        main()
    elif len(sys.argv) == 2:
        main(int(sys.argv[1]))
    elif len(sys.argv) == 3:
        main(int(sys.argv[1]), int(sys.argv[2]))
