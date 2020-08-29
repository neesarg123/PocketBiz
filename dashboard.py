import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from decimal import *
from operator import add
from functools import reduce
import os.path

BS = 'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css'
app = dash.Dash(external_stylesheets=[BS])


def reformat_dollar_amount(dollars):
    data_chars = [l for l in str(dollars).split('.')[0]]
    cents = str(dollars).split('.')[1]
    for i in range(len(data_chars) - 4, -1, -3):
        data_chars[i] = str(data_chars[i]) + ','
    return ''.join(data_chars) + "." + cents


def pre_process():
    # Data frames
    global inventory_df, transactions_df

    here = os.path.dirname(os.path.abspath(__file__))

    inventory_filename = os.path.join(here, 'Inventory.xlsx')
    transactions_filename = os.path.join(here, 'Transactions.xlsx')

    if os.path.isfile(inventory_filename):
        inventory_df = pd.read_excel(inventory_filename, ignore_index=True)
    else:
        print("No Inventory File Was Found!")
        inventory_df = pd.DataFrame([])

    if os.path.isfile(transactions_filename):
        transactions_df = pd.read_excel(transactions_filename, ignore_index=True)
    else:
        print("No Transactions File Was Found!")
        transactions_df = pd.DataFrame([])


def do_calculations():
    global total_inventory_amount, total_revenue_amount, total_tax_amount
    # Calculations
    inventory_df['Quantity'] = inventory_df['Quantity'].astype(dtype=float)
    inventory_df['S.Price'] = np.array(inventory_df['S.Price'], dtype=float)

    sp_times_quant = [s * q for s, q in zip(list(inventory_df['S.Price']), list(inventory_df['Quantity']))]
    total_inventory_amount = Decimal(reduce(add, sp_times_quant)).quantize(Decimal('.01'))
    total_inventory_amount = reformat_dollar_amount(total_inventory_amount)

    transactions_df['Total'] = transactions_df['Total'].fillna(0.0)
    total_revenue_amount = Decimal(reduce(add, list(transactions_df['Total']))).quantize(Decimal('.01'))
    total_revenue_amount = reformat_dollar_amount(total_revenue_amount)

    transactions_df['Tax'] = transactions_df['Tax'].fillna(0.0)
    total_tax_amount = Decimal(reduce(add, list(transactions_df['Tax']))).quantize(Decimal('.01'))
    total_tax_amount = reformat_dollar_amount(total_tax_amount)


def daily_graph():
    global date_fig, today_total

    pre_process()
    do_calculations()

    # Daily Graph
    dates_trans_df = transactions_df.groupby('Date').sum()
    date_graph_x = dates_trans_df.index
    date_graph_y = dates_trans_df['Total']
    # Today's Total
    today_total = Decimal(date_graph_y[-1]).quantize(Decimal('.01'))
    today_total = reformat_dollar_amount(today_total)

    date_fig = go.Figure(data=[go.Bar(x=date_graph_x, y=date_graph_y,
                                      hovertemplate="Sale: $%{y}<extra></extra>")])
    # Customize aspect
    date_fig.update_traces(marker_color='rgb(235, 52, 91)', marker_line_color='rgb(8,48,107)',
                           marker_line_width=1.5, opacity=0.6)
    date_fig.layout.plot_bgcolor = 'rgb(255, 255, 255)'
    date_fig.update_layout(
        xaxis= dict(
            tickvals=date_graph_x,
        ),
        hoverlabel=dict(
            bgcolor="rgb(255, 81, 69)",
            font_size=20,
            font_family="Rockwell"
        )
    )

    return date_fig


def monthly_graph():
    global t2, months_fig

    pre_process()
    do_calculations()

    # Monthly Graph
    t2 = transactions_df.copy()
    t2['Date'] = t2['Date'].astype(str)
    t2['Date'] = [d[:7] for d in t2['Date']]
    months_trans_df = t2.groupby('Date').sum()

    months_graph_x = months_trans_df.index
    months_graph_y = months_trans_df['Total']

    months_fig = go.Figure(data=[go.Bar(x=months_graph_x, y=months_graph_y,
                                        hovertemplate="Sale: $%{y}<extra></extra>")])
    # Customize aspect
    months_fig.update_traces(marker_color='rgb(235, 52, 91)', marker_line_color='rgb(8,48,107)',
                             marker_line_width=1.5, opacity=0.6)
    months_fig.layout.plot_bgcolor = 'rgb(255, 255, 255)'
    months_dict = {
        '01': 'January',
        '02': 'February',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }
    months_labels = [months_dict[m[5:7]] + ', ' + m[0:4] for m in months_graph_x]
    months_fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=months_graph_x,
            ticktext=months_labels
        ),
        hoverlabel=dict(
            bgcolor="rgb(255, 81, 69)",
            font_size=20,
            font_family="Rockwell"
        )
    )

    return months_fig


def yearly_graph():
    global years_fig

    pre_process()
    do_calculations()

    # Yearly Graph
    t2['Date'] = transactions_df['Date']
    t2['Date'] = t2['Date'].astype(str)
    t2['Date'] = [d[:4] for d in t2['Date']]
    years_trans_df = t2.groupby('Date').sum()

    years_graph_x = years_trans_df.index
    years_graph_y = years_trans_df['Total']

    years_fig = go.Figure(data=[go.Bar(x=years_graph_x, y=years_graph_y,
                                       hovertemplate="Sale: $%{y}<extra></extra>")])
    # Customize aspect
    years_fig.update_traces(marker_color='rgb(235, 52, 91)', marker_line_color='rgb(8,48,107)',
                            marker_line_width=1.5, opacity=0.6)
    years_fig.layout.plot_bgcolor = 'rgb(255, 255, 255)'

    years_fig.update_layout(
        xaxis=dict(
            tickvals=years_graph_x,
        ),
        hoverlabel=dict(
            bgcolor="rgb(255, 81, 69)",
            font_size=20,
            font_family="Rockwell"
        )
    )

    return years_fig


def pie_chart():
    global pie_fig

    pre_process()
    do_calculations()

    # Pie Chart - Cash/Credit
    cash_count = transactions_df.where(transactions_df['P.Type'] == 'CASH').count()
    cash_val = cash_count['P.Type']
    credit_count = transactions_df.where(transactions_df['P.Type'] == 'CREDIT').count()
    credit_val = credit_count['P.Type']
    labels = ['CASH', 'CREDIT']
    values = [cash_val, credit_val]
    pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, text=values,
                                     hovertemplate="# of Transactions: %{text}")])
    pie_fig.layout.plot_bgcolor = 'rgb(255, 255, 255)'
    pie_fig.update_layout(
        title_text="CASH/CREDIT Transactions",
        hoverlabel=dict(
            bgcolor="rgb(25, 212, 128)",
            font_size=18,
            font_family="Rockwell"
        ))

    return pie_fig


def top_ten_table():
    global table_df
    # Top Ten Selling Items Table
    item_names_and_frequency = []
    for name in transactions_df['Name']:
        if name != 'Misc.':  # don't want to count these
            count = transactions_df['Name'].where(transactions_df['Name'] == name).count()
            if [name, count] not in item_names_and_frequency:
                item_names_and_frequency.append([name, count])

    # sorting the list by greatest to least sale frequency
    item_names_and_frequency.sort(key=lambda x: x[1], reverse=True)
    # only want top 10
    item_names_and_frequency = item_names_and_frequency[:10]
    # creating table data frame
    table_df = pd.DataFrame(
        {
            '🔥 Top 10 Selling Items': [item[0] for item in item_names_and_frequency],
            'Count': [item[1] for item in item_names_and_frequency]
        }
    )


pre_process()
do_calculations()
daily_graph()
monthly_graph()
yearly_graph()
top_ten_table()


def serve_layout():
    return html.Div(style={'margin-left': '0px', 'margin-right': '0px',
                           'margin-top': '0px', 'margin-bottom': '0px', 'backgroundColor': 'rgb(255, 255, 255)'},
                    children=[
                        dbc.Navbar(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.NavbarBrand("| BizTracker", className="ml-2",
                                                                style={'font-family': 'verdana',
                                                                       'font-size': '150%',
                                                                       'font-weight': 'bold'}),
                                                width=3),

                                        dbc.Col(
                                            html.Div(
                                                children=[
                                                    html.H5(children=["Today's Sales: $" + str(today_total)],
                                                            style={'color': 'orange',
                                                                   'font-family': 'impact',
                                                                   'font-size': '150%'}, id='today_sale'),
                                                ],
                                                style={'padding-left': '80px', 'padding-top': '10px'}
                                            ))
                                    ],
                                    no_gutters=True,
                                ),
                            ],
                            color="#191a1a",
                            dark=True,
                            fixed='top',
                            style={'opacity': '0.9'}
                        ),

                        html.Div(
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Card([
                                                dbc.CardHeader("TOTAL INVENTORY"),
                                                dbc.CardBody(
                                                    [
                                                        html.H4("$ " + str(total_inventory_amount),
                                                                className="card-title", id='total_inv_amount'),

                                                    ]
                                                ),
                                            ], color="primary",
                                                inverse=True)
                                        ),

                                        dbc.Col(
                                            dbc.Card([
                                                dbc.CardHeader("TOTAL SALE"),
                                                dbc.CardBody(
                                                    [
                                                        html.H4("$ " + str(total_revenue_amount),
                                                                className="card-title", id='total_rev_amount'),

                                                    ]
                                                ),
                                            ], color="success",
                                                inverse=True)
                                        ),

                                        dbc.Col(
                                            dbc.Card([
                                                dbc.CardHeader("TOTAL TAX"),
                                                dbc.CardBody(
                                                    [
                                                        html.H4("$ " + str(total_tax_amount), className="card-title",
                                                                id='total_tax_amount'),

                                                    ]
                                                ),
                                            ], color="danger",
                                                inverse=True)
                                        )
                                    ],
                                    style={'padding-right': '0px', 'padding-left': '0px', 'margin-right': '0px',
                                           'margin-left': '0px', 'padding-top': '22px', 'padding-bottom': '24px',
                                           'borderBottom': 'thick lightgrey solid'},
                                ),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='sale_dropdown',
                                                options=[
                                                    {'label': 'Daily Sales', 'value': 'Day'},
                                                    {'label': 'Monthly Sales', 'value': 'Mon'},
                                                    {'label': 'Yearly Sales', 'value': 'Yea'},
                                                ],
                                                style={'width': '300px', 'padding-left': '30px'},
                                                value='Day',
                                                clearable=False,
                                                searchable=False,
                                            ), style={'backgroundColor': 'rgb(255, 255, 255)',
                                                      'padding-top': '10px'},
                                        ),
                                    ]
                                ),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Graph(id='sale_graph')
                                        )
                                    ]
                                ),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dash_table.DataTable(
                                                id='table',
                                                columns=[{"name": i, "id": i} for i in table_df.columns],
                                                data=table_df.to_dict('records'),
                                                style_as_list_view=True,
                                                style_header={'backgroundColor': 'rgb(255, 255, 255)',
                                                              'color': 'rgb(50, 187, 191)',
                                                              'height': '50px',
                                                              'font_family': 'impact',
                                                              'textAlign': 'center',
                                                              'font_size': '24px'},
                                                style_cell={
                                                    'backgroundColor': 'rgb(255, 255, 255)',
                                                    'font_family': 'impact',
                                                    'font_size': '20px',
                                                    'color': 'rgb(201, 52, 172)',
                                                    'textAlign': 'center',
                                                    'whiteSpace': 'normal',
                                                    'height': 'auto',
                                                },
                                                style_table={'height': '450px', 'width': '785px', 'overflowY': 'auto'},
                                            ),
                                            style={'padding-right': '0px', 'padding-left': '0px', 'margin-left': '0px',
                                                   'margin-right': '0px'}
                                        ),

                                        dbc.Col(
                                            dcc.Graph(
                                                id='pie',
                                                figure=pie_chart()
                                            ),
                                            style={'padding-left': '0px', 'margin-left': '0px',
                                                   'borderTop': 'thin lightgrey solid'}
                                        )
                                    ],
                                    style={'margin-bottom': '0px !important', 'padding-top': '0px',
                                           'padding-bottom': '0px', 'padding-right': '0px', 'padding-left': '0px'}
                                )
                            ],
                            style={'margin-bottom': '0px !important', 'padding-top': '60px',
                                   'padding-bottom': '0px',
                                   'padding-right': '0px', 'padding-left': '0px'},
                        ),
                    ])


app.title = 'Live Dashboard'
app.layout = serve_layout


@app.callback(
    [dash.dependencies.Output('sale_graph', 'figure'),
     dash.dependencies.Output('total_inv_amount', 'children'),
     dash.dependencies.Output('total_rev_amount', 'children'),
     dash.dependencies.Output('total_tax_amount', 'children'),
     dash.dependencies.Output('today_sale', 'children'),
     dash.dependencies.Output('table', 'columns'),
     dash.dependencies.Output('table', 'data')
     ],
    [dash.dependencies.Input('sale_dropdown', 'value')]
)
def update_graph(type_value):
    top_ten_table()
    columns = [{"name": i, "id": i} for i in table_df.columns]
    data = table_df.to_dict('records')
    pie_chart()

    if str(type_value) == 'Day':
        return [daily_graph(), "$ " + str(total_inventory_amount), "$ " + str(total_revenue_amount), "$ " +
                str(total_tax_amount), "Today's Sales: $" + str(today_total), columns, data]
    elif str(type_value) == 'Mon':
        return [monthly_graph(), "$ " + str(total_inventory_amount), "$ " +
                str(total_revenue_amount), "$ " + str(total_tax_amount), "Today's Sales: $" + str(today_total),
                columns, data]
    else:
        return [yearly_graph(), "$ " + str(total_inventory_amount), "$ " + str(total_revenue_amount), "$ " +
                str(total_tax_amount), "Today's Sales: $" + str(today_total),  columns, data]


app.run_server(debug=True)
