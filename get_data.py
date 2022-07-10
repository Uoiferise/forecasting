import pandas as pd
import datetime as dt


def get_data():
    historical_data = pd.read_excel(
        'data/data.xlsx',
        sheet_name='historical_data')  # Historical cost and sales data
    historical_data.rename(columns={'Номенклатура': 'nomenclature'}, inplace=True)

    current_balances = pd.read_excel(
        'data/data.xlsx',
        sheet_name='current_balances')  # Information from the inventory and orders report

    current_orders = pd.read_excel(
        'data/data.xlsx',
        sheet_name='current_orders')  # Information about current orders
    order_numbers = list(int(i) for i in current_orders['ЗП'].unique())
    nomenclature_name = current_orders['Номенклатура'].unique()
    current_orders_dict = {}
    for name in nomenclature_name:
        result = {}
        df = current_orders.loc[current_orders['Номенклатура'] == name][['ЗП', 'Зак. ост.']]
        for order in order_numbers:
            result[order] = df.loc[df['ЗП'] == order]['Зак. ост.'].sum()

        current_orders_dict[name] = result

    order_numbers_dict = {}
    for order in order_numbers:
        d = str(current_orders.loc[current_orders['ЗП'] == order]['Пост план'].values[0])
        if d == 'NaT':
            order_numbers_dict[order] = dt.date(2122,
                                                12,
                                                31)
        else:
            order_numbers_dict[order] = dt.date(int(d.split('-')[0]),
                                                int(d.split('-')[1]),
                                                int(d.split('-')[2][:2]))

    sorted_tuples = sorted(order_numbers_dict.items(), key=lambda item: item[1])
    sorted_order_numbers_dict = {k: v for k, v in sorted_tuples}

    stock_sales = pd.read_excel(
        'data/data.xlsx',
        sheet_name='stock_sales')  # Already posted for sale

    stock_available = pd.read_excel(
        'data/data.xlsx',
        sheet_name='stock_available')  # Available for sale

    print('Данные прочитаны успешно!')
    print('-'*20)
    return historical_data, current_balances, current_orders_dict, \
        sorted_order_numbers_dict, stock_sales, stock_available
