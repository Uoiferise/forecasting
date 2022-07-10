import datetime
from dateutil.relativedelta import *


def stock_forecasting(period, cost, sale, stock_0, minimal_cost_stock, order_numbers_dict, current_orders_dict):
    stock = [stock_0]
    color = []
    buy = 0

    date_forecasting = datetime.date.today()

    for i in range(period):
        color.append([])

        date_forecasting = date_forecasting + relativedelta(months=+1)

        if stock[i] <= sum(cost[i:i+minimal_cost_stock]):
            flag = False
        else:
            flag = True

        orders = []
        for k in order_numbers_dict.keys():
            order_date = order_numbers_dict[k]

            if order_date < datetime.date.today() or current_orders_dict.get(k, 0) == 0:
                continue
            elif order_date < date_forecasting:
                orders.append(k)
            else:
                break

        value = stock[i]
        if len(orders) > 0:
            start_date = date_forecasting + relativedelta(months=-1)
            end_date = date_forecasting
            delta_all = (end_date - start_date).days

            for index, item in enumerate(orders):
                order_date = order_numbers_dict[item]
                delta_order = (order_date - start_date).days

                coeff_1 = float(delta_order / delta_all)
                start_date = order_date

                if flag:
                    value -= cost[i] * coeff_1 + sale[i] * coeff_1
                else:
                    value -= cost[i] * coeff_1

                if value > 0 and flag:
                    color[i].append('g')
                elif value > 0:
                    color[i].append('y')
                else:
                    color[i].append('r')
                    value = 0

                value += current_orders_dict[item]
                current_orders_dict[item] = 0

                if index == len(orders) - 1:
                    delta_end = (end_date - order_date).days
                    coeff_2 = float(delta_end / delta_all)

                    if flag:
                        value -= cost[i] * coeff_2 + sale[i] * coeff_2
                    else:
                        value -= cost[i] * coeff_2

                    if value > 0 and flag:
                        color[i].append('g')
                    elif value > 0:
                        color[i].append('y')
                    else:
                        color[i].append('r')
                        value = 0
        else:
            if flag:
                value -= cost[i] + sale[i]
            else:
                value -= cost[i]

            if value > 0 and flag:
                color[i].append('g')
            elif value > 0:
                color[i].append('y')
            else:
                color[i].append('r')
                value = 0

        stock.append(float(value))
        color = list(map(lambda x: ''.join(x), color))

    return stock[1:], color, float(buy)
