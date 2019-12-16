from processing import constants
import plotly.graph_objects as go
import pandas as pd

ann_x = [2011, 2017, 2014, 2018, 2011, 2018, 2018,
             2018, 2008, 2009, 2009, 2013, 2009, 2018,
             2009, 2018, 2015, 2013, 2015, 2017, 2010,
             2010, 2009,
             ]
ann_y = [9.7, 11.8, 1.3, 26.5, 15.7, 7.08, 20.4, 33, 26.5, 22.6, -1, 22, 22.7, 15.4, 21, 16.7, 19.5, 7.2, 7.8, 15,
         14.3, 7.4, 10]


def plot_delay(delay_by_airports, delay_by_states, delay_type, text):
    """
    This function plots the dynamic delay graph with the given delay data in terms of airports and states.
    Note the delay_by_airports is a list of dataFrames, and each dataFrame represents the delay data for all airports in
    different years/months. Each dataFrame in this list has the columns as
    ['name', 'type', 'municipality', 'iso_region', 'iata_code',
       'latitude_deg', 'longitude_deg', 'ORIGIN', 'ORIGIN_COUNT', 'DEP_DELAY',
       'text', 'size']
    the delay_by_states is a list of input dataFrame with the column as
    ['iso_region', 'DEP_DELAY', 'ORIGIN_COUNT']
    *******************************************
    delay_type should have the values in
        ["DEP_DELAY", "ARR_DELAY"],
    specifying whether we want the departure delay or the arrival delay.
    the text here is used for the text showing in the graph
    @param delay_by_airports: input flight delays for airport
    @type delay_by_airports: list
    @param delay_by_states:  input flight delays for states
    @type delay_by_states: list
    @param delay_type: input type with value in ["DEP_DELAY", "ARR_DELAY"]
    @type delay_type: str
    @param text: input text in the graph
    @type text: str
    @return: None
    @rtype: None
    """
    assert isinstance(delay_by_airports, list)
    assert isinstance(delay_by_states, list)
    assert isinstance(delay_type, str)
    assert delay_type in ["DEP_DELAY", "ARR_DELAY"]
    assert isinstance(text, str)

    fig = go.Figure(
        data=
        [
            go.Choropleth(
                locations=delay_by_states[0]['iso_region'],
                z=delay_by_states[0][delay_type].astype(int),
                locationmode='USA-states',
                colorscale='Portland',
                autocolorscale=False,
                marker_line_color='white',
                colorbar=dict(x=1.15),
                colorbar_title=delay_type + " (min)",
                zmin=0, zmax=25
            ),
            go.Scattergeo(
                locationmode='USA-states',
                lon=delay_by_airports[0]['longitude_deg'],
                lat=delay_by_airports[0]['latitude_deg'],
                mode='markers',
                text=delay_by_airports[0]['text'],
                name='',
                marker=
                dict(
                    size=delay_by_airports[0]['size'],
                    colorscale='Portland',
                    color=delay_by_airports[0][delay_type],
                    colorbar=dict(x=1.0),
                    line_color='rgb(255,255,255)',
                    line_width=0.5,
                    cmin=0,
                    cmax=25,
                    showscale=False
                ),
            )
        ],
        layout=go.Layout(
            title=constants.MONTH_ENG_LIST[0] + " (" + constants.MONTH_LIST[0] + ") " + text if len(delay_by_states) == 2
            else str(constants.YEAR_LIST[0]) + " " + text,
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
        frames=[go.Frame(
            name=str(i),
            data=[go.Choropleth(
                locations=delay_by_states[i]['iso_region'],
                z=delay_by_states[i][delay_type].astype(int),
                locationmode='USA-states',
                colorscale='Portland',
                autocolorscale=False,
                marker_line_color='white',
                colorbar_title=delay_type + " (min)",
                zmin=0, zmax=25
            ),
                go.Scattergeo(
                    locationmode='USA-states',
                    lon=delay_by_airports[i]['longitude_deg'],
                    lat=delay_by_airports[i]['latitude_deg'],
                    mode='markers',
                    text=delay_by_airports[i]['text'],
                    name='',
                    marker=
                    dict(
                        size=delay_by_airports[i]['size'],
                        colorscale='Portland',
                        color=delay_by_airports[i][delay_type],
                        colorbar=dict(x=1.0),
                        line_color='rgb(255,255,255)',
                        line_width=0.5,
                        cmin=0,
                        cmax=25,
                        showscale=False
                    ),
                )],
            baseframe='0',
            layout=go.Layout(title_text=
                             constants.MONTH_ENG_LIST[i] + " (" + constants.MONTH_LIST[i] + ") " + text if len(delay_by_states) == 3
                             else str(2009 + i) + " " + text),
        ) for i in range(len(delay_by_states))]

    )

    fig.show()


def plot_airline_history_delay(df_total_delay, carrier_list):
    """
    This function is used to plot the yearly average delay line graph for different airlines from 2009-2018
    :param df_total_delay: the input delay data for airlines
    :type df_total_delay: pd.DataFrame
    :param carrier_list: the input list for all of the airlines
    :type carrier_list: list
    :return:
    """
    assert isinstance(df_total_delay, pd.DataFrame)
    assert isinstance(carrier_list, list)

    annotation_list = []
    fig = go.Figure()
    for i in range(len(carrier_list)):
        fig.add_trace(go.Scatter(
            x=sorted(list(set(df_total_delay['year'].to_list()))),
            y=df_total_delay[df_total_delay['OP_CARRIER'] == carrier_list[i]]['total delay'].to_list(),
            mode='lines+markers',
            name=constants.AIRLINE_FULLNAME_MAP[carrier_list[i]],
            line=dict(color=constants.COLORS[i]),
        ), )
        annotation_list.append(go.layout.Annotation(
            x=ann_x[i],
            y=ann_y[i],
            xref="x",
            yref="y",
            text=constants.AIRLINE_FULLNAME_MAP[carrier_list[i]],
            ax=20,
            ay=-20
        ), )
    fig.update_layout(
        autosize=False,
        width=950,
        height=650,
        title_text='2009-2018 US Domestic Airlines Average Delay History',
        xaxis=dict(
            dtick=1,
            title='Year (2009-2018)',
        ),
        yaxis=dict(
            title='Average Total Delay (min)'
        ),
        #     annotations=annotation_list,
    )
    fig.show()


def plot_delay_top10_airlines(df_total_delay, carrier_list):
    """
    This function is used to plot the average delay over the past 10 years for 10 us airlines that are still working.
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
        if carrier_list[i] in constants.AIRLINE_CODES_STILL_WORKING:
            fig.add_trace(go.Box(
                y=df_total_delay[df_total_delay['OP_CARRIER'] == carrier_list[i]]['total delay'].to_list(),
                name=constants.AIRLINE_FULLNAME_MAP[carrier_list[i]]
            ))
    fig.update_layout(
        title_text='10 US Domestic Airlines Average Delay Box Plot',
    )
    fig.show()