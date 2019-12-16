from processing import constants
import plotly.graph_objects as go
import pandas as pd


def plot_cancellation_history(cancel_airline, carrier_list):
    """
    This function is used to plot the line graph for the cancellation history in terms of different US airlines.
    :param cancel_airline: input airline cancellation summary for all us airlines
    :type cancel_airline: pd.DataFrame
    :param carrier_list: input airline name list
    :type carrier_list: list
    :return:
    """
    assert isinstance(cancel_airline, pd.DataFrame)
    assert isinstance(carrier_list, list)
    for d in cancel_airline:
        isinstance(d, pd.DataFrame)
    for s in carrier_list:
        isinstance(s, str)

    fig = go.Figure()
    for i, carrier in enumerate(carrier_list):
        fig.add_trace(go.Scatter(
            x=constants.YEAR_LIST,
            y=cancel_airline[cancel_airline['OP_CARRIER'] == carrier]['cancellation_ratio'].to_list(),
            mode='lines+markers',
            name=constants.AIRLINE_FULLNAME_MAP[carrier],
            line=dict(color=constants.COLORS[i]),
            text=''
        ), )
    fig.update_layout(
        autosize=False,
        width=950,
        height=650,
        title_text='2009-2018 US Domestic Airlines Cancellation History',
        xaxis=dict(
            dtick=1,
            title='Year (2009-2018)',
        ),
        yaxis=dict(
            title='Cancellation Rate'
        ),
    )
    fig.show()


def plot_cancellation_reasons(code_a, code_b, code_c, code_d):
    """
    This function is used to plot the bar graph for the cancellation reasons each year from 2009-2018
    :param code_a: yearly count of the reason a from 2009-2018
    :type code_a: list
    :param code_b: yearly count of the reason b from 2009-2018
    :type code_b: list
    :param code_c: yearly count of the reason c from 2009-2018
    :type code_c: list
    :param code_d: yearly count of the reason d from 2009-2018
    :type code_d: list
    :return: 
    """
    assert isinstance(code_a, list)
    assert isinstance(code_b, list)
    assert isinstance(code_c, list)
    assert isinstance(code_d, list)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(2009, 2019)),
        y=code_a,
        name='Airline/Carrier',
    ))
    fig.add_trace(go.Bar(
        x=list(range(2009, 2019)),
        y=code_b,
        name='Weather',
    ))
    fig.add_trace(go.Bar(
        x=list(range(2009, 2019)),
        y=code_c,
        name='National Air System',
    ))
    fig.add_trace(go.Bar(
        x=list(range(2009, 2019)),
        y=code_d,
        name='Security',
    ))

    fig.update_layout(
        title_text='Cancellation Reason Analysis',  # title of plot
        xaxis_title_text='Year (2009-2018)',  # xaxis label
        yaxis_title_text='Cancellation Times',  # yaxis label
        bargap=0.2,
        bargroupgap=0.1
    )

    fig.show()


def plot_cancellation_heatmap_with_states(data, state_list):
    """
    This function is used to plot the heat map of cancellation rates in terms of different states and months.
    :param data: the input cancellation data for different months and states
    :type data: list
    :param state_list: the input state list that we will follow
    :type state_list: list
    :return:
    """
    assert isinstance(data, list)
    for i in data:
        assert isinstance(i, list)
    assert isinstance(state_list, list)
    for s in state_list:
        assert isinstance(s, str)

    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=state_list,
        y=constants.MONTH_LIST,
        colorbar=dict(title='Times', thickness=5),
        colorscale='Portland'
    ))
    fig.update_layout(
        autosize=False,
        height=450,
        width=950,
        margin=go.layout.Margin(
            l=0,
            r=0,
            pad=0
        ),
        yaxis=dict(
            dtick=1
        ),
        xaxis=dict(
            dtick=2,
            tickangle=0,
        ),
        title_text='2009-2018 Total Cancellation Rate with respect to month and state',
        xaxis_title_text='States',  # xaxis label
        yaxis_title_text='Month',  # yaxis label
    )
    fig.show()


def plot_cancellation_by_state_and_month(df_cancel_stat):
    """
    This function is to plot the dynamic cancellation map graph for different states in different months.
    :param df_cancel_stat: input cancellation data frame
    :type df_cancel_stat: pd.DataFrame
    :return:
    """
    assert isinstance(df_cancel_stat, pd.DataFrame)

    fig = go.Figure(data=
    [
        go.Choropleth(
            locations=df_cancel_stat[df_cancel_stat['month'] == constants.MONTH_LIST[0]]['iso_region'].to_list(),
            z=df_cancel_stat[df_cancel_stat['month'] == constants.MONTH_LIST[0]]['count'].to_list(),
            locationmode='USA-states',
            colorscale='Portland',
            autocolorscale=False,
            marker_line_color='white',
            colorbar_title="Cancellation Rate",
            zmin=0, zmax=0.07
        )],
        layout=go.Layout(
            title='2009 - 2018 January (01) US Airline Cancellation Rate',
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
                         ])],
        ),

        frames=[go.Frame(data=[go.Choropleth(
            locations=df_cancel_stat[df_cancel_stat['month'] == constants.MONTH_LIST[0]]['iso_region'].to_list(),
            z=df_cancel_stat[df_cancel_stat['month'] == constants.MONTH_LIST[i]]['count'],
            locationmode='USA-states',
            colorscale='Portland',
            autocolorscale=False,
            marker_line_color='white',
            colorbar_title="Cancellation Rate",
            zmin=0, zmax=0.07
        )],
            layout=go.Layout(title_text="2009 - 2018 " + constants.MONTH_ENG_LIST[i] + " (" + constants.MONTH_LIST[
                i] + ")" + " US Airline Cancellation Rate"),
        ) for i in range(12)
        ]
    )

    fig.show()