from processing import constants
import plotly.graph_objects as go
import pandas as pd


def plot_count(count_by_airports, count_by_states, count_type, text):
    """
    This function plots the dynamic flight count graph with the given flight number count data in terms of airports and states.
    Note the count_by_airports is a list of dataFrames, and each dataFrame represents the flight count data for all airports in
    different years/months. Each dataFrame in this list has the columns as
    ['name', 'type', 'municipality', 'iso_region', 'iata_code',
       'latitude_deg', 'longitude_deg', 'ORIGIN', 'ORIGIN_COUNT'or'DEST_COUNT', 'DEP_DELAY' or 'ARR_DELAY',
       'text', 'size']
    the count_by_states is a list of input dataFrame with the column as
    ['iso_region', 'ORIGIN_COUNT' or 'DEST_COUNT]
    *******************************************
    count_type should have the values in
        ["ORIGIN_COUNT", "DEST_COUNT"],
    specifying whether we want to count the origin flight number or the destination number for different airports/states
    the text here is used for the text showing in the graph
    @param count_by_airports: input flight number for airport
    @type count_by_airports: list
    @param count_by_states:  input flight number for states
    @type count_by_states: list
    @param count_type: input type with value in  ["ORIGIN_COUNT", "DEST_COUNT"]
    @type count_type: str
    @param text: input text in the graph
    @type text: str
    @return: None
    @rtype: None
    """
    assert isinstance(count_by_airports, list)
    assert isinstance(count_by_states, list)
    assert isinstance(count_type, str)
    assert isinstance(text, str)

    fig = go.Figure(data=
    [
        go.Choropleth(
            locations=count_by_states[0]['iso_region'],
            z=count_by_states[0][count_type].astype(int),
            locationmode='USA-states',
            colorscale='Portland',
            autocolorscale=False,
            marker_line_color='white',
            colorbar=dict(x=1.15),
            colorbar_title="By State",
            zmin=0,
            zmax=7 * 10 ** 5
        ),
        go.Scattergeo(
            locationmode='USA-states',
            lon=count_by_airports[0]['longitude_deg'],
            lat=count_by_airports[0]['latitude_deg'],
            mode='markers',
            text=count_by_airports[0]['text'],
            name='',
            marker=
            dict(
                size=count_by_airports[0]['size'],
                colorscale='Portland',
                color=count_by_airports[0][count_type],
                colorbar=dict(x=1.0),
                colorbar_title="By Airports",
                line_color='rgb(255,255,255)',
                line_width=0.5,
                cmin=0,
                cmax=4 * 10 ** 5
            ),
        )
    ],
        layout=go.Layout(
            title=constants.MONTH_ENG_LIST[0] + " (" + constants.MONTH_LIST[0] + ") " + text if len(count_by_states) == 12 else str(
                constants.YEAR_LIST[0]) + " " + text,
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=False,
            ),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None]),
                         dict(label="Pause",
                              method='animate',
                              args=['', {'mode': 'immediate'}]),
                         ])]
        ),
        frames=[
            go.Frame(data=[
                go.Choropleth(
                    locations=count_by_states[i]['iso_region'],
                    z=count_by_states[i][count_type].astype(int),
                    locationmode='USA-states',
                    colorscale='Portland',
                    autocolorscale=False,
                    marker_line_color='white',
                    colorbar=dict(x=1.15),
                    colorbar_title="By State",
                    zmin=0,
                    zmax=7 * 10 ** 5
                ),
                go.Scattergeo(
                    locationmode='USA-states',
                    lon=count_by_airports[i]['longitude_deg'],
                    lat=count_by_airports[i]['latitude_deg'],
                    mode='markers',
                    text=count_by_airports[i]['text'],
                    name='',
                    marker=
                    dict(
                        size=count_by_airports[i]['size'],
                        colorscale='Portland',
                        color=count_by_airports[i][count_type],
                        colorbar=dict(x=1.0),
                        colorbar_title="By Airports",
                        line_color='rgb(255,255,255)',
                        line_width=0.5,
                        cmin=0,
                        cmax=4 * 10 ** 5
                    ),

                )],
                layout=go.Layout(title_text=
                                 constants.MONTH_ENG_LIST[i] + " (" + constants.MONTH_LIST[i] + ") " + text if len(count_by_states) == 12
                                 else str(2009 + i) + " " + text),
            ) for i in range(len(count_by_states))
        ])

    fig.show()


def plot_airline_history_count(df_total_delay, carrier_list):
    """
    This function is used to plot the yearly flight count graph for different airlines from 2009-2018
    :param df_total_delay: the input delay data for airlines
    :type df_total_delay: pd.DataFrame
    :param carrier_list: the input list for all of the airlines
    :type carrier_list: list
    :return:
    """
    assert isinstance(df_total_delay, pd.DataFrame)
    assert isinstance(carrier_list, list)

    fig = go.Figure()
    for i in range(len(carrier_list)):
        fig.add_trace(go.Scatter(
            x=sorted(list(set(df_total_delay['year'].to_list()))),
            y=df_total_delay[df_total_delay['OP_CARRIER'] == carrier_list[i]]['counts'].to_list(),
            mode='lines+markers',
            name=constants.AIRLINE_FULLNAME_MAP[carrier_list[i]],
            line=dict(color=constants.COLORS[i]),
            text=''
        ), )
    fig.update_layout(
        autosize=False,
        width=950,
        height=650,
        title_text='2009-2018 US Domestic Airlines Flights Number History',
        xaxis=dict(
            dtick=1,
            title='Year (2009-2018)',
        ),
        yaxis=dict(
            title='Number of Flights'
        ),
    )
    fig.show()
