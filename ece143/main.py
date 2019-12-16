import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import processing.constants as constants
from processing.airport import extract_us_airport, data_prepare, count_cancellation_by_airport
from processing.airline import prepare_airline_delay_data, get_airline_route_by_state, count_cancellation_by_airline
from processing.flight import get_flight_data_by_year
from processing.operations import merge

from plot import plot_count, plot_delay, plot_cancellation, plot_DelayReason


def plot_dep_count_by_airport_and_state_yearly():
    """
    This function plots the yearly departure flight count from 2009-2018 for different airports and states
    """
    df_dep_count_list_by_year, df_dep_count_by_state_list_by_year = data_prepare(constants.TARGET_COUNT,
                                                                                 constants.DIRECTION_DEPARTURE,
                                                                                 constants.TIME_YEAR)

    plot_count.plot_count(df_dep_count_list_by_year, df_dep_count_by_state_list_by_year, "ORIGIN_COUNT",
               "US Domestic Airline Departure Count (Origin)")


def plot_arr_count_by_airport_and_state_yearly():
    """
    This function plots the yearly arrival flight count from 2009-2018 for different airports and states
    """
    df_dep_count_list_by_year, df_dep_count_by_state_list_by_year = data_prepare(constants.TARGET_COUNT,
                                                                                 constants.DIRECTION_ARRIVAL,
                                                                                 constants.TIME_YEAR)
    plot_count.plot_count(df_dep_count_list_by_year, df_dep_count_by_state_list_by_year, "DEST_COUNT",
               "US Domestic Airline Arrival Count (DEST)")


def plot_throughpupt_by_apiports_and_state_yearly():
    """
    This function plots the throughput for different airports and states from 2009-2018.
    :return:
    """
    df_count_list, df_count_by_state_list = data_prepare(constants.TARGET_THROUGHPUT,
                                                         constants.DIRECTION_ARRIVAL,
                                                         constants.TIME_YEAR)
    plot_count.plot_count(df_count_list, df_count_by_state_list, "COUNT", "US Domestic Airline Throughput")


def plot_dep_delay_by_airports_and_state_yearly():
    """
    This function will plot the average yearly departure delay for airports and states
    :return:
    """
    df_dep_delay_list_by_year, df_dep_delay_by_state_list_by_year = data_prepare(constants.TARGET_DELAY,
                                                                                 constants.DIRECTION_DEPARTURE,
                                                                                 constants.TIME_YEAR)
    plot_delay.plot_delay(df_dep_delay_list_by_year, df_dep_delay_by_state_list_by_year, "DEP_DELAY",
               "US Domestic Airline Departure Delay (Origin)")


def plot_arr_delay_by_airports_and_state_yearly():
    """
    This function plots the average yearly arrival delay for airports and states
    :return:
    """
    df_arr_delay_list_by_year, df_arr_delay_by_state_list_by_year = data_prepare(constants.TARGET_DELAY,
                                                                                 constants.DIRECTION_ARRIVAL,
                                                                                 constants.TIME_YEAR)
    plot_delay.plot_delay(df_arr_delay_list_by_year, df_arr_delay_by_state_list_by_year, "ARR_DELAY",
               "US Domestic Airline ARR Delay (DEST)")


def plot_dep_delay_by_airports_and_state_monthly():
    """
    This function will plot the average monthly departure delay for airports and states
    :return:
    """
    df_dep_delay_list_by_month, df_dep_delay_by_state_list_by_month = data_prepare(constants.TARGET_DELAY,
                                                                                   constants.DIRECTION_DEPARTURE,
                                                                                   constants.TIME_MONTH)
    plot_delay.plot_delay(df_dep_delay_list_by_month, df_dep_delay_by_state_list_by_month, "DEP_DELAY",
               "US Domestic Airline Departure Delay (Origin)")


def plot_arr_delay_by_airports_and_state_monthly():
    """
    This function will plot the average monthly arrival delay for airports and states
    :return:
    """
    df_arr_delay_list_by_month, df_arr_delay_by_state_list_by_month = data_prepare(constants.TARGET_DELAY,
                                                                                   constants.DIRECTION_ARRIVAL,
                                                                                   constants.TIME_MONTH)
    plot_delay.plot_delay(df_arr_delay_list_by_month, df_arr_delay_by_state_list_by_month, "ARR_DELAY",
               "US Domestic Airline Arrival Delay (Dest)")


def plot_airline_history():
    """
    This function calls three functions and plots three graphs.
    It plots the history flight average delay, flight count for all airlines from 2009-2018;
    It plots the average history delay for the 10 airlines that still work nowadays.
    :return:
    """
    df_total_delay = prepare_airline_delay_data()
    carrier_list = constants.AIRLINE_CODES_STILL_WORKING
    plot_delay.plot_airline_history_delay(df_total_delay, carrier_list)
    plot_count.plot_airline_history_count(df_total_delay, carrier_list)
    plot_delay.plot_delay_top10_airlines(df_total_delay, carrier_list)


def plot_airline_routes():
    """
    This function plots the route distributions over states for all airlines.
    :return:
    """
    df_airport = pd.read_csv(constants.AIRPORT_DATA_PATH)
    df_us_airport = extract_us_airport(df_airport)
    df_2018 = get_flight_data_by_year(2018, ['OP_CARRIER', 'ORIGIN', 'DEST'])
    df_2018_origin = merge(df_us_airport, df_2018, 'iata_code', 'ORIGIN')
    df_2018_dest = merge(df_us_airport, df_2018, 'iata_code', 'DEST')

    fig = make_subplots(rows=3, cols=4,
                        specs=[[{"type": "domain"} for i in range(4)] for j in range(3)],
                        subplot_titles=[constants.AIRLINE_FULLNAME_MAP[k] for k in
                                        constants.AIRLINE_CODES_STILL_WORKING],
                        vertical_spacing=0.01,
                        )

    for idx, airline in enumerate(constants.AIRLINE_CODES_STILL_WORKING):
        df_region_route_cnts = get_airline_route_by_state(df_2018_origin, df_2018_dest, airline)
        fig.add_trace(
            go.Pie(
                labels=df_region_route_cnts['Region'],
                values=df_region_route_cnts['route_counts'],
            ),
            row=idx // 4 + 1, col=idx % 4 + 1
        )
    fig.update_layout(
        autosize=False,
        width=900,
        height=800,
        title_text='2018 US Domestic Airline Origin and Destination Statistics (by Region)',
        margin=dict(b=0),
    )
    fig.show()


def plot_cancellation_history():
    """
    This function calls internal functions and plots several graphs:
    1. plots the cancellation rate history for all airlines.
    2. plots the reasons distribution for flight cancellations for each year from 2009-2018
    3. plots the cancellation rate of different states over different months.
    4. plots the dynamic cancellation rate change over months for all states in US.
    :return:
    """
    # plot the cancellation history trend
    cancel_airline = count_cancellation_by_airline()
    carrier_list = constants.AIRLINE_CODES_STILL_WORKING
    plot_cancellation.plot_cancellation_history(cancel_airline, carrier_list)

    # plot the cancellation reasons
    df_all, df_cancel, code_a, code_b, code_c, code_d = count_cancellation_by_airport()
    plot_cancellation.plot_cancellation_reasons(code_a, code_b, code_c, code_d)

    # plot cancellation rate with  respect to month and state¶
    df_all_sum = df_all.groupby(['iso_region', 'month']).agg({'counts': sum}).rename_axis(
        ['iso_region', 'month']).reset_index()
    df_cancel_clean = df_cancel[['FL_DATE', 'iso_region']]
    df_cancel_clean['month'] = df_cancel_clean['FL_DATE'].str.split('-').str[1]
    df_cancel_clean = df_cancel_clean.drop(columns=['FL_DATE'])
    df_cancel_clean = df_cancel_clean.groupby(['iso_region', 'month']).size().reset_index(name='count')
    df_cancel_clean = df_cancel_clean.groupby(['iso_region', 'month']).agg({'count': sum}).rename_axis(
        ['iso_region', 'month']).reset_index()
    df_cancel_stat = pd.merge(df_all_sum, df_cancel_clean, on=['iso_region', 'month'])
    df_cancel_stat['count'] /= df_cancel_stat['counts']

    state_list = sorted(list(set(df_cancel['iso_region'].to_list())))
    data = [[] for i in range(12)]
    for i in range(df_cancel_stat.shape[0]):
        month = int(df_cancel_stat.iloc[i, 1])
        if df_cancel_stat.iloc[i, 0] not in state_list:
            data[month - 1].append(0)
        else:
            data[month - 1].append(df_cancel_stat.iloc[i, 3])

    plot_cancellation.plot_cancellation_heatmap_with_states(data, state_list)
    plot_cancellation.plot_cancellation_by_state_and_month(df_cancel_stat)


def plot_delay_reasons_distributions():
    """
    This function is used to plot the distributions for different delay reasons.
    :return:
    """
    plot_DelayReason.PlotPieDemon()
