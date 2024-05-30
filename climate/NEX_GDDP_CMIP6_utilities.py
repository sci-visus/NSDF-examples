from OpenVisus import *


def build_file_name(model: str, variable: str, scenario: str, variant: str, version: str, year: int, extension: str) -> str:
    year_str = '' if year == 0 else f'_{year}'
    version_str = '' if version == '' else f'_{version}'
    variable_str = '' if variable == '' else f'{variable}_'

    # 'gn' needs to change depending on the model
    return f'{variable_str}day_{model}_{scenario}_{variant}_gn{year_str}{version_str}.{extension}'


def build_url(base_url: str, model: str, variable: str, scenario: str, variant: str) -> str:
    return f'{base_url}{model}/{scenario}/{variant}/{variable}/'


def create_directory(path: str) -> None:
    if os.path.exists(path):
        print(f'Directory exists: {path}')
    else:
        os.mkdir(path)
        print(f'Directory created: {path}')


def get_timestep(year: int, day: int) -> int:
    return day + (year * 365)


