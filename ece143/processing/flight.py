import pandas as pd
import processing.constants as constants
from processing.operations import read_csv_file


def get_flight_data_by_year(year, used_cols=[]):
    """
    This function get the flight data for the given year and only returns given columns
    @param year: input year
    @type year: int
    @param used_cols: the input columns list
    @type used_cols: list
    @return: flight dataframe
    @rtype: pd.DataFrame
    """
    assert isinstance(year, int)
    assert isinstance(used_cols, list)

    df_year = read_csv_file(constants.ROOT + str(year) + '.csv')
    if not used_cols:
        return df_year
    return df_year[used_cols]


def get_flight_data_by_month(i, used_cols):
    """
    This function get the flight data for the ith month and only returns given columns
    @param i: the month index
    @type i: int
    @param used_cols: the input columns list
    @type used_cols: list
    @return: flight dataframe
    @rtype: pd.DataFrame
    """
    assert isinstance(i, int)
    assert 0 <= i <= 11
    assert isinstance(used_cols, list)

    df_month = pd.DataFrame()
    for year in constants.YEAR_LIST:
        df_year = get_flight_data_by_year(year, used_cols)
        # not cancelled
        df_year = df_year[df_year['CANCELLED'] != 1]
        # compute for month column
        df_year['month'] = df_year['FL_DATE'].str.split('-').str[1]
        # choose a specific column
        curr = df_year[df_year['month'] == constants.MONTH_LIST[i]]
        # combine
        df_month = df_month.append(curr)
    return df_month