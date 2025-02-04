from pathlib import Path
import logging
import re
import io
import numpy as np
import pandas as pd
import argparse


sample_number_regex = re.compile('S(\d+)_')
realization_number_regex = re.compile(r'_(\d+)(?:\.xdd)?$')

expected_column_sizes = np.asarray([
            11, 13, 5, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 13, 12
        ])
ids_of_interest = np.genfromtxt('ids.txt', dtype='str').tolist()
expected_line_size = expected_column_sizes.sum()
expected_column_count = len(expected_column_sizes)
month_column = 3
id_column = 1
year_column = 2
demand_column = 4
shortage_column = 17
outflow_column = 31
control_location_column = 33
id_column_name = 'structure_id'
year_column_name = 'year'
month_column_name = 'month'
demand_column_name = 'demand'
shortage_column_name = 'shortage'
outflow_column_name = 'river_outflow'
control_location_column_name = 'control_location'
id_column_type = object
year_column_type = np.uint16
month_column_type = object
demand_column_type = np.uint32
shortage_column_type = np.uint32
outflow_column_type = np.uint32
control_location_column_type = object
sample_column_name = 'sample'
sample_column_type = np.uint16
realization_column_name = 'realization'
realization_column_type = np.uint8
outputs_path = '/scratch/ah986/rival_framings_demand/xdd_parquet_flow'


def xxd_to_parquet(file_path):
    path = Path(file_path)
    try:
        sample_number = int(sample_number_regex.search(path.stem).group(1))
        realization_number = int(realization_number_regex.search(path.stem).group(1))
    except (IndexError, AttributeError):
        logging.error(f"Unable to parse sample or realization number from file name: {path.stem}.")
        return False
    # stream will hold CSV of interesting data
    stream = io.StringIO()
    # read the file line by line
    with open(path, 'r') as file:
        id_start = np.sum(expected_column_sizes[:id_column])
        id_end = id_start + expected_column_sizes[id_column]
        for line in file:
            if line[id_start:id_end].strip() in ids_of_interest:
                # check the line length; note that the line ending counts as a character, hence the +1
                if len(line) != (expected_line_size + 1):
                    # unexpected line length; you need to double check the expected column sizes
                    logging.error(
                        f"Unexpected line length: {len(line)} instead of {expected_line_size}:\n{line}"
                    )
                    return False
                # split data by character counts
                data = []
                position = 0
                for count in expected_column_sizes:
                    data.append(line[position:(position + count)].strip())
                    # no spaces between columns
                    position += count
                if len(data) != expected_column_count:
                    # unexpected number of columns; you need to double check your data and settings
                    logging.error(
                        f"Unexpected column count: {len(data)} instead of {expected_column_count}:\n{line}"
                    )
                    return False
                # only keep non-total rows
                if not data[month_column].casefold().startswith('tot'):
                    stream.write(
                        ','.join(
                            [data[i] for i in [
                                id_column,
                                year_column,
                                month_column,
                                demand_column,
                                shortage_column,
                                outflow_column,
                                control_location_column
                            ]]
                        )
                    )
                    stream.write('\n')
    stream.seek(0)

    df = pd.read_csv(
        stream,
        header=None,
        names=[
            id_column_name,
            year_column_name,
            month_column_name,
            demand_column_name,
            shortage_column_name,
            outflow_column_name,
            control_location_column_name
        ],
        dtype={
            id_column_name: id_column_type,
            year_column_name: year_column_type,
            month_column_name: month_column_type,
            demand_column_name: demand_column_type,
            shortage_column_name: shortage_column_type,
            outflow_column_name: outflow_column_type,
            control_location_column_name: control_location_column_type
        }
    )

    stream.close()

    df[sample_column_name] = sample_column_type(sample_number)
    df[realization_column_name] = realization_column_type(realization_number)
    df.to_parquet(
        Path(f'{outputs_path}/S{sample_number}_{realization_number}.parquet'),
        engine='pyarrow',
        compression='gzip'
    )
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert .xdd to .parquet')
    parser.add_argument('file_path', type=str,
                        help='path to .xdd file')
    args = parser.parse_args()
    xxd_to_parquet(args.file_path)
