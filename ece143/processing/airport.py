from processing import constants
import pandas as pd
from processing.operations import count, aggregate, average, merge,read_csv_file
from processing.flight import get_flight_data_by_year, get_flight_data_by_month


def extract_us_airport(df):
    """
    This function takes an airport dataFrame with 18 columns, removes the outliers such as NA,
    only keeps "US" airport data by the "country" column, and returns a new dataFrame with 7 useful columns:
    `name,type,municipality,iso_region,iata_code,latitude_deg,longitude_deg`
    @param df: the input original worldwide airports data
    @type df: pd.DataFrame
    @return: the cleaned US airport data
    @rtype:  pd.DataFrame
    """
    required_cols = ['name', 'type', 'municipality', 'iso_region', 'iata_code', 'latitude_deg', 'longitude_deg']
    assert isinstance(df, pd.DataFrame)
    assert {'iso_country'}.issubset(df.columns)
    assert set(required_cols).issubset(df.columns)

    df_airport = df.dropna(subset=['iata_code'])
    df_airport_us = df_airport[df_airport['iso_country'] == 'US']
    df_airport_us['iso_region'] = df_airport_us['iso_region'].str.upper().str.split('-').str.get(-1)
    df_airport = pd.DataFrame(df_airport_us, columns=required_cols)
    return df_airport


def prepare_delay(df, direction):
    """
    This function is used to prepare delay data used for flight analysis in terms of airports and states. Specially, the
    direction specifies if we are calculating the "DEPARTURE" or "ARRIVAL" delay.
    @param df: input flight dataFrame
    @type df: pd.DataFrame
    @param direction: input direction for analysis
    @type direction: str
    @return: delay dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(direction, str)
    assert direction == constants.DIRECTION_ARRIVAL or direction == constants.DIRECTION_DEPARTURE

    if direction == constants.DIRECTION_DEPARTURE:
        airport_type = 'ORIGIN'
        delay_type = 'DEP_DELAY'
        count_type = "ORIGIN_COUNT"
    elif direction == constants.DIRECTION_ARRIVAL:
        airport_type = 'DEST'
        delay_type = 'ARR_DELAY'
        count_type = "DEST_COUNT"

    df_delay = df[df['CANCELLED'] != 1]
    df_us_airport = read_csv_file(constants.CLEANED_AIRPORT_DATA_PATH)

    # ORIGIN counts_origin
    df_cnts = count(df_delay, airport_type, count_type)

    # ORIGIN DEP_DELAY
    df_delay_cnts = aggregate(df_delay, airport_type, delay_type)

    # ORIGIN DEP_DELAY counts_origin
    df_delay_cnts = merge(df_cnts, df_delay_cnts, airport_type, airport_type)
    # flights>50
    df_delay_cnts = df_delay_cnts[df_delay_cnts[count_type] > 50]

    # airport-info ORIGIN DEP_DELAY counts_origin
    df_delay_by_airport = merge(df_us_airport, df_delay_cnts, 'iata_code', airport_type).dropna()
    # state total DEP_DELAY
    df_delay_by_state = df_delay_by_airport.groupby(['iso_region']) \
        .agg({delay_type: sum}) \
        .rename_axis('iso_region') \
        .reset_index()
    # state flights
    df_cnts_by_state = df_delay_by_airport.groupby(['iso_region']) \
        .agg({count_type: sum}) \
        .rename_axis('iso_region') \
        .reset_index()

    # state flights total DEP_DELAY
    df_delay_cnts_by_state = pd.merge(df_delay_by_state, df_cnts_by_state, on='iso_region')

    # state flights average DEP_DELAY
    df_delay_by_state = average(df_delay_cnts_by_state, delay_type, count_type)

    # airport-info average DEP_DELAY
    df_delay_by_airport = average(df_delay_by_airport, delay_type, count_type)

    return df_delay_by_airport, df_delay_by_state


def prepare_count(df, direction):
    """
    This function is used to prepare flight count data used for flight analysis in terms of airports and states.
    Specially, the direction specifies if we are calculating the "DEPARTURE" or "ARRIVAL" flight number count.
    @param df: input flight dataFrame
    @type df: pd.DataFrame
    @param direction: input direction for analysis
    @type direction: str
    @return: count dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(direction, str)
    assert direction == constants.DIRECTION_ARRIVAL or direction == constants.DIRECTION_DEPARTURE

    if direction == constants.DIRECTION_DEPARTURE:
        airport_type = 'ORIGIN'
        count_type = "ORIGIN_COUNT"
    elif direction == constants.DIRECTION_ARRIVAL:
        airport_type = 'DEST'
        count_type = "DEST_COUNT"

    df_delay = df[df['CANCELLED'] != 1]
    df_us_airport = read_csv_file(constants.CLEANED_AIRPORT_DATA_PATH)

    df_origin_counts = count(df_delay, airport_type, count_type)
    df_origin = merge(df_us_airport, df_origin_counts, 'iata_code', airport_type).dropna()
    df_origin_by_state = aggregate(df_origin, 'iso_region', count_type)
    return df_origin, df_origin_by_state


def prepare_throughput(df):
    """
    This function is used to prepare throughput count data used for flight analysis in terms of airports and states.
    @param df: input flight dataFrame
    @type df: pd.DataFrame
    @return: throughput dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(df, pd.DataFrame)

    df_dep_cnts_by_airport, df_dep_cnts_by_state = prepare_count(df, constants.DIRECTION_DEPARTURE)
    df_arr_cnts_by_airport, df_arr_cnts_by_state = prepare_count(df, constants.DIRECTION_ARRIVAL)
    df_throughput_by_state = pd.merge(df_dep_cnts_by_state, df_arr_cnts_by_state, on='iso_region')
    df_throughput_by_state[constants.TARGET_COUNT] = df_throughput_by_state['ORIGIN_COUNT'] + df_throughput_by_state['DEST_COUNT']

    df_throughput = pd.merge(df_dep_cnts_by_airport, df_arr_cnts_by_airport[['DEST', 'DEST_COUNT']], left_on='ORIGIN',
                             right_on='DEST')
    df_throughput[constants.TARGET_COUNT] = df_throughput['ORIGIN_COUNT'] + df_throughput['DEST_COUNT']
    return df_throughput, df_throughput_by_state


def data_prepare(target, direction, dtime):
    """
    This function is the interface function for the client to use to get data when specifying different parameters.
    For example:
    delay_airports, delay_states = data_prepare(constants.TARGET_DELAY, constants.DIRECTION_DEPARTURE, constants.TIME_YEAR)
    will return the yearly delay data for both the airports and states.
    @param target: the input target str specifying which target we want to get data for: delay, count, throughput
    @type target: str
    @param direction: the input direction specifying whether we want to get data for "DEPARTURE" or "ARRIVAL" flights.
    @type direction: str
    @param dtime: specifying whether we want to get yearly data or monthly data
    @type dtime: str
    @return: dataFrame
    @rtype: pd.DataFrame
    """
    assert isinstance(target, str)
    assert isinstance(direction, str)
    assert isinstance(dtime, str)
    assert target in [constants.TARGET_COUNT, constants.TARGET_DELAY, constants.TARGET_THROUGHPUT]
    assert direction == constants.DIRECTION_ARRIVAL or direction == constants.DIRECTION_DEPARTURE
    assert dtime == constants.TIME_MONTH or dtime == constants.TIME_YEAR

    df_by_airport = []
    df_by_state = []
    used_cols = ['FL_DATE', 'ORIGIN', 'DEST', 'DEP_DELAY', 'ARR_DELAY', 'CANCELLED']
    if direction == constants.DIRECTION_DEPARTURE:
        count_type = "ORIGIN_COUNT"
    elif direction == constants.DIRECTION_ARRIVAL:
        count_type = "DEST_COUNT"

    if dtime == constants.TIME_YEAR:
        max_iter = 10
    else:
        max_iter = 12
    for i in range(max_iter):
        if dtime == constants.TIME_YEAR:
            df_flight = get_flight_data_by_year(i + constants.YEAR_LIST[0], used_cols)
        else:
            df_flight = get_flight_data_by_month(i, used_cols)

        # decide which target we need analyze
        if target == constants.TARGET_DELAY:
            df, df_state = prepare_delay(df_flight, direction)
        elif target == constants.TARGET_COUNT:
            df, df_state = prepare_count(df_flight, direction)
        elif target == constants.TARGET_THROUGHPUT:
            df, df_state = prepare_throughput(df_flight)
        else:
            print('ERROR!')

        # add information for hover text
        df['text'] = 'Airport Name: ' + df['name'] + ' (' + df['iata_code'] + ')' + \
                     '<br>' + 'Type: ' + df['type'].str.replace('_', ' ').str.title() + \
                     '<br>' + 'Municipality: ' + df['municipality'] + \
                     '<br>' + 'State: ' + df['iso_region'] + \
                     '<br>' + 'Flights: ' + df[count_type].astype(str)
        if target == constants.TARGET_DELAY and direction == constants.DIRECTION_DEPARTURE:
            df['text'] = df['text'] + '<br>' + 'Departure Delay (Min): ' + round(df['DEP_DELAY'], 2).astype(str)
        elif target == constants.TARGET_DELAY and direction == constants.DIRECTION_ARRIVAL:
            df['text'] = df['text'] + '<br>' + 'Arrive Delay (Min): ' + round(df['ARR_DELAY'], 2).astype(str)
        df['size'] = list(map(lambda x: constants.TYPES[x], df['type']))
        df_by_airport.append(df)
        df_by_state.append(df_state)
    return df_by_airport, df_by_state


def count_cancellation_by_airport():
    """
    This function returns the statistics for cancellation reasons and cancellation records for different airports
    """
    code_a = []
    code_b = []
    code_c = []
    code_d = []
    all_records = pd.DataFrame()
    cancel_records = pd.DataFrame()

    df_us_airport = read_csv_file(constants.CLEANED_AIRPORT_DATA_PATH)

    for year in constants.YEAR_LIST:
        df_cur = get_flight_data_by_year(year, [])

        df_all = df_cur[['FL_DATE', 'ORIGIN']]
        df_all['month'] = df_all['FL_DATE'].str.split('-').str[1]
        df_all = merge(df_us_airport, df_all, 'iata_code', 'ORIGIN')
        df_all = df_all[['iso_region', 'month']].dropna()
        df_all = df_all.groupby(['iso_region', 'month']).size().reset_index(name='counts')
        all_records = all_records.append(df_all)
        del df_all

        df_cancel = df_cur[df_cur['CANCELLED'] != 0]
        df_cancel = merge(df_us_airport, df_cancel, 'iata_code', 'ORIGIN')
        df_cancel = df_cancel[['FL_DATE', 'iso_region', 'CANCELLATION_CODE']].dropna()
        df_cancel['FL_DATE'] = df_cancel['FL_DATE'].str.rsplit(pat='-', n=1).str[0]

        a = df_cancel[df_cancel['CANCELLATION_CODE'] == 'A'].shape[0]
        b = df_cancel[df_cancel['CANCELLATION_CODE'] == 'B'].shape[0]
        c = df_cancel[df_cancel['CANCELLATION_CODE'] == 'C'].shape[0]
        d = df_cancel[df_cancel['CANCELLATION_CODE'] == 'D'].shape[0]
        code_a.append(a)
        code_b.append(b)
        code_c.append(c)
        code_d.append(d)
        cancel_records = cancel_records.append(df_cancel.reset_index(drop=True))
    return all_records, cancel_records, code_a, code_b, code_c, code_d

