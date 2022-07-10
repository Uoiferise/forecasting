import datetime as dt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from get_data import get_data
from dateutil.relativedelta import *
from stock_forecasting import stock_forecasting


def forecasting():
    historical_data, current_balances, current_orders_dict,\
        order_numbers_dict, stock_sales, stock_available = get_data()

    def equation(x, y):
        # model initialization
        regression_model = LinearRegression()

        # fit the data(train the model)
        regression_model.fit(x, y)

        # predict
        y_predicted = regression_model.predict(x)

        # model evaluation
        rmse = mean_squared_error(y, y_predicted)
        r2 = r2_score(y, y_predicted)

        result = {
            'a': regression_model.coef_[0][0],
            'b': regression_model.intercept_[0],
            'Root mean squared error of the model': rmse,
            'R^2': r2,
            'len_y': len(y)
        }
        return result

    nomenclatures = current_balances['Номенклатура'].unique()

    def get_number(text, func):
        result = ''
        while True:
            try:
                result = abs(func(input(text)))
            except ValueError:
                print('Неверный формат!')
            else:
                break
            finally:
                print()
        return result

    mean_period = get_number(
        text='Введите период расчета средних значений (Примеры: 1; 2; ..): ',
        func=int)

    def equation_dict(data_name):
        result = {}
        for name in nomenclatures:
            df = historical_data.loc[historical_data.nomenclature == name][[data_name]]
            df.reset_index(drop=True, inplace=True)

            cost = [float(value) for value in df[data_name].values]
            if len(cost) > mean_period:
                y = np.array([
                    [sum(cost[i:i + mean_period]) / mean_period] for i in range(len(cost) - mean_period + 1)
                ])
                x = np.array([[i] for i in range(1, len(y) + 1)])

                if len(x) >= 10:
                    result[name] = equation(x, y)
                else:
                    result[name] = {'R^2': '-'}
            else:
                result[name] = {'R^2': '-'}
        return result

    equation_cost_dict = equation_dict('Собст расход')
    equation_sale_dict = equation_dict('Продажи')

    report_data = current_balances

    # Adding columns to current orders.
    for k, v in order_numbers_dict.items():
        report_data[f'Заказ №{k} ({v.strftime("%d.%m.%Y")})'] = [current_orders_dict.get(name, {0: 0}).get(k, 0)
                                                                 for name in current_balances['Номенклатура']]

    report_data['Расх. R^2'] = [equation_cost_dict[name]['R^2'] for name in current_balances['Номенклатура']]

    # report_data['Ур. расх.'] = [
    #     '-' if equation_cost_dict[name]['R^2'] == '-'
    #     else f'y = {round(equation_cost_dict[name]["a"], 2)}*x + ({round(equation_cost_dict[name]["b"], 2)})'
    #     for name in current_balances['Номенклатура']
    # ]

    report_data['Прод. R^2'] = [equation_sale_dict[name]['R^2'] for name in current_balances['Номенклатура']]

    # report_data['Ур. прод.'] = [
    #     '-' if equation_sale_dict[name]['R^2'] == '-'
    #     else f'y = {round(equation_sale_dict[name]["a"], 2)}*x + ({round(equation_sale_dict[name]["b"], 2)})'
    #     for name in current_balances['Номенклатура']
    # ]

    good_cost_r2 = get_number(
        text='Введите допустимое значение R^2 для собственного расхода (Примеры: 0.75; ..): ',
        func=float)
    good_sale_r2 = get_number(
        text='Введите допустимое значение R^2 для продаж (Примеры: 0.75; ..): ',
        func=float)

    def method(name_dict, good_r2):
        result = {}
        for name in nomenclatures:
            if name_dict[name]['R^2'] == '-':
                result[name] = 'СЗ'
            elif name_dict[name]['R^2'] < good_r2:
                result[name] = 'СЗ'
            else:
                result[name] = 'ЛР'
        return result

    method_cost,  method_sale = method(equation_cost_dict, good_cost_r2), method(equation_sale_dict, good_sale_r2)
    report_data['Расх. метод'] = [method_cost[name] for name in current_balances['Номенклатура']]
    report_data['Прод. метод'] = [method_sale[name] for name in current_balances['Номенклатура']]

    # Creating a function for forecasting costs, sales, stocks
    def analysis(nomenclature_name, period, minimal_cost_stock):
        result = [
            [],    # for cost
            [],    # for sale
            [],    # for stock
            [],    # for buy
            []     # for color
        ]

        df_cost = historical_data.loc[historical_data.nomenclature == nomenclature_name][['Собст расход']]
        df_cost.reset_index(drop=True, inplace=True)
        cost = [float(value) for value in df_cost['Собст расход'].values]

        df_sale = historical_data.loc[historical_data.nomenclature == nomenclature_name][['Продажи']]
        df_sale.reset_index(drop=True, inplace=True)
        sale = [float(value) for value in df_sale['Продажи'].values]

        # Cost forecasting
        if method_cost[name] == 'ЛР':
            for i in range(1, period + minimal_cost_stock + 1):
                x = equation_cost_dict[nomenclature_name]['len_y'] + i
                y = equation_cost_dict[nomenclature_name]['a'] * x + \
                    equation_cost_dict[nomenclature_name]['b']    # predicted mean cost

                predicted_cost = (y * mean_period) - sum(cost[-1*mean_period+1:])
                if predicted_cost < 0:
                    predicted_cost = 0

                result[0].append(round(predicted_cost, 1))
                cost.append(predicted_cost)
        else:
            for _ in range(period+minimal_cost_stock):
                mean_cost = sum(cost[-3:])/len(cost[-3:])
                predicted_cost = mean_cost * 1.05    # mean cost * coefficient
                result[0].append(round(predicted_cost, 1))

        # Sale forecasting
        if method_sale[name] == 'ЛР':
            for i in range(1, period + minimal_cost_stock + 1):
                x = equation_sale_dict[nomenclature_name]['len_y'] + i
                y = equation_sale_dict[nomenclature_name]['a'] * x + \
                    equation_sale_dict[nomenclature_name]['b']    # predicted mean sale

                predicted_sale = (y * mean_period) - sum(sale[-1*mean_period+1:])
                if predicted_sale < 0:
                    predicted_sale = 0

                result[1].append(round(predicted_sale, 1))
                sale.append(predicted_sale)
        else:
            for _ in range(period+minimal_cost_stock):
                mean_sale = sum(sale[-3:])/len(cost[-3:])
                predicted_sale = mean_sale * 1.05    # mean sale * coefficient
                result[1].append(round(predicted_sale, 1))

        # Stock forecasting
        stock_0 = current_balances.loc[current_balances['Номенклатура'] == nomenclature_name][['Св ост']].values[0]

        stock, color, buy = stock_forecasting(
            period=period,
            cost=result[0],
            sale=result[1],
            stock_0=stock_0,
            minimal_cost_stock=minimal_cost_stock,
            order_numbers_dict=order_numbers_dict,
            current_orders_dict=current_orders_dict.get(nomenclature_name, {0: 0})
        )

        result[2] = stock
        result[3] = buy
        result[4] = color

        return result

    delivery_time = 3   # months
    necessary_stock = 9   # months
    forecasting_period = delivery_time + necessary_stock
    minimal_stock_for_cost = 5    # months
    analysis_dict = {}
    for name in nomenclatures:
        analysis_dict[name] = analysis(nomenclature_name=name,
                                       period=forecasting_period,
                                       minimal_cost_stock=minimal_stock_for_cost)

    def get_historical_info(data_names, period=3):
        result = {}
        for name in nomenclatures:
            result_list = []
            for name_data in data_names:
                df_cost = historical_data.loc[historical_data.nomenclature == name][[name_data]]
                df_cost.reset_index(drop=True, inplace=True)
                cost = [float(value) for value in df_cost[name_data].values]

                if len(cost[-period:]) == 0:
                    result_list.append([0.0 for _ in range(period)])
                elif len(cost[-period:]) == 1:
                    result_list.append([0.0, 0.0] + cost[-period:])
                elif len(cost[-period:]) == 2:
                    result_list.append([0.0] + cost[-period:])
                else:
                    result_list.append(cost[-period:])

            result[name] = result_list
        return result

    historical_info_dict = get_historical_info(data_names=['Собст расход', 'Продажи'])

    # Creating columns: cost, sale, stock
    date_start = dt.date.today()
    column_name = ('cost', 'sale', 'stock')
    for n in range(3):
        if n < 2:
            date = date_start + relativedelta(months=-3)
            for col in range(3):
                report_data[f'{column_name[n]} {date.strftime("%b %Y")}'] = \
                    [historical_info_dict[name][n][col] for name in current_balances['Номенклатура']]
                date = date + relativedelta(months=+1)

        date = date_start
        for num in range(1, forecasting_period + 1):
            date = date + relativedelta(months=+1)
            report_data[f'{column_name[n]} {date.strftime("%b %Y")}'] = \
                [analysis_dict[name][n][num-1] for name in current_balances['Номенклатура']]

    # Creating column: buy
    report_data['Кол-во к заказу'] = [analysis_dict[name][3] for name in current_balances['Номенклатура']]

    orders = len(order_numbers_dict.keys())

    print('Анализ проделан успешно!')
    print('-'*20)
    return report_data, analysis_dict, forecasting_period, orders
