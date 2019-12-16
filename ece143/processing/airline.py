import pandas as pd
from processing import constants
from processing.operations import count, aggregate, average, merge, read_csv_file
from processing.airport import get_flight_data_by_year, extract_us_airport


def prepare_airline_delay_data():
    """
    This function returns the delay data for different airlines.
    @return: the delay dataFrame
    @rtype: pd.DataFrame
    """
    df = pd.DataFrame()
    used_cols = []
    for year in constants.YEAR_LIST:
        curr = get_flight_data_by_year(year, used_cols)
        df_delay = total_delay(curr)
        df_delay['year'] = str(year)
        df = df.append(df_delay)
    return df


def total_delay(df):
    """
    This function calculates the average total delay which is the sum of the DEP_DELAY and ARR_DELAY for different airlines.
    @param df: input airline delay data dataFrame
    @type df: pd.DataFrame
    @return: the dataFrame which shows the average the delay for different airlines
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)

    df_cur = df[df['CANCELLED'] != 1]
    df_cur['total delay'] = df_cur['DEP_DELAY'] + df_cur['ARR_DELAY']
    # carrier total delay
    df_cur_valid = df_cur[['OP_CARRIER', 'total delay']]
    # carrier counts
    df_airline_counts = count(df_cur_valid, 'OP_CARRIER', 'counts')
    # carrier total delay
    df_airline_delay = aggregate(df_cur_valid, 'OP_CARRIER', 'total delay')
    # merge
    df_airline_merge_delay = merge(df_airline_delay, df_airline_counts, 'OP_CARRIER', 'OP_CARRIER')
    # average
    df_airline_avg_delay = average(df_airline_merge_delay, 'total delay', 'counts')

    return df_airline_avg_delay


def get_airline_route_by_state(df_origin, df_dest, airline):
    """
    This function takes all of the origin flights and destination flights as input. It calculates the distribution of
    the flight routes in terms of different states. For example, for the given airline = "AA", it will return the flight
    number distribution to all reachable states.
    @param df_origin: the input origin dataFrame
    @type df_origin: pd.DataFrame
    @param df_dest: the input destination dataFrame
    @type df_dest: pd.DataFrame
    @param airline: the given airline code
    @type airline: str
    @return: flight number distribution dataFrame for this airline.
    @rtype: pd.DataFrame
    """
    assert isinstance(df_origin, pd.DataFrame)
    assert isinstance(df_dest, pd.DataFrame)
    assert isinstance(airline, str)

    us_division = read_csv_file(constants.US_REGION_DIVISION_DATA_PATH)
    df_us_airport = read_csv_file(constants.CLEANED_AIRPORT_DATA_PATH)

    df_airport_origin_cnts  = df_origin[df_origin['OP_CARRIER']==airline]['ORIGIN']\
        .value_counts().rename_axis('iata_code').reset_index(name='origin_counts')
    df_airport_dest_cnts  = df_dest[df_dest['OP_CARRIER']==airline]['DEST']\
        .value_counts().rename_axis('iata_code').reset_index(name='dest_counts')
    df_airport_route_cnts = merge(df_airport_origin_cnts, df_airport_dest_cnts,'iata_code','iata_code')
    df_airport_route_cnts['route_counts'] = df_airport_route_cnts['origin_counts']+df_airport_route_cnts['dest_counts']
    df_airport_route_cnts = merge(df_airport_route_cnts,df_us_airport,'iata_code', 'iata_code')[['iata_code','route_counts','iso_region']]
    df_state_route_cnts = aggregate(df_airport_route_cnts, 'iso_region','route_counts')
    df_region_route_cnts = pd.merge(df_state_route_cnts, us_division, left_on='iso_region',right_on = 'State Code')
    df_region_route_cnts = aggregate(df_region_route_cnts, 'Region','route_counts')

    return df_region_route_cnts


def count_cancellation_by_airline():
    """
    This function returns the statistics for cancellation reasons and cancellation records for
    different airlines
    @return: None
    @rtype: None
    """
    cancel_airline = pd.DataFrame()
    for year in constants.YEAR_LIST:
        df_cur = get_flight_data_by_year(year, [])

        df_airline = df_cur['OP_CARRIER'].value_counts().rename_axis('OP_CARRIER').reset_index(name='total_cnts')
        df_cancel = df_cur[df_cur['CANCELLED'] != 0]
        df_cancel_airline = df_cancel['OP_CARRIER'].value_counts().rename_axis('OP_CARRIER').reset_index(
            name='cancellation_cnts')
        df_cancel_rate_airline = pd.merge(df_airline, df_cancel_airline, on='OP_CARRIER')
        df_cancel_rate_airline['cancellation_ratio'] = df_cancel_rate_airline['cancellation_cnts'] / \
                                                       df_cancel_rate_airline['total_cnts']
        df_cancel_rate_airline['year'] = year
        cancel_airline = cancel_airline.append(df_cancel_rate_airline.reset_index(drop=True))
    return cancel_airline