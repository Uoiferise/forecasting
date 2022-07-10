# Описание работы программы по прогнозированию запасов
## 1. Общее объяснение функционирования программы
Структура программы состоит из следующих функционально разделенных блоков:
-	get_data;
-	forecasting;
-	create_report.

Отдельный скрипт get_data отвечает исключительно за считывание данных из файла data. После считывания файла, функция get_data возвращает готовые датафреймы, которые передаются в функцию forecasting для дальнейшего выполнения программы. Файл data подготавливается заранее и должен содержать следующие рабочие листы:
-	historical_data (на данном рабочем листе файла с помощью надстройки Power Query собрана информация об исторических значениях расходов и продаж по конкретной группе материальных ценностей; информация представляется в виде умной таблицы);
-	current_balances (на данном рабочем листе файла с помощью надстройки Power Query собрана информация о текущих остатках по рассматриваемой группе товаров; на основе номенклатуры представленной на данном листе и будет проводиться расчет заказа и прогнозирование запасов; информация представляется в виде умной таблицы);
-	current_orders (на данном рабочем листе файла с помощью надстройки Power Query собрана информация о текущих заказах по рассматриваемой группе товаров; стоит заранее проверить правильность отражение прогнозируемых сроков поставок текущих заказов, т.к. это может повлиять на результаты прогнозирования; информация представляется в виде умной таблицы);

Стоит отметить, что информация в файле data собирается автоматически, благодаря настроенным запросам Power Query к стандартным выгрузкам отчетов из 1С. При создании нового отчета по прогнозированию запасов, будет достаточно сделать новые выгрузки, в файле data информация обновится автоматически.

Отдельный скрипт forecasting отвечает за процесс обработки и анализа данных. После выполнения своего скрипты, функция выдает конечный датафрейм, который передается в функцию create_report.

Отдельный скрипт create отвечает за процесс создание итогового отчета со всей визуализацией. На выходе получается готовый отчет «!Report».

## 2. Подробное объяснение работы get_data
...

## 3. Подробное объяснение работы forecasting
Как говорилось ранее, в данном скрипте реализован весь процесс анализа данных. Он состоит из нескольких последовательных этапов:
-	расчет уравнений линейной регрессий для каждой отдельной номенклатуры;
-	отбор методологий по прогнозированию собственных расходов и продаж;
-	прогнозирование собственных расходов и продаж в соответствии с выбранными методологиями и периодом прогнозирования;
-	помесячный расчет остатков на основе спрогнозированных собственных расходов и продаж;
-	расчет кол-ва к заказу.

Расчет уравнений линейной регрессии строится на основе скользящих средних значений. Кол-во для вычисления средних значений задается с помощью ввода общего значения. Рекомендуется использовать минимум 6 месячные средние значения. Данная особенность обусловлена тем, что отдельные расходы и продажи носят зачастую хаотичный порядок, однако, довольно часто значение средних расходов ведет себя закономерно прямой линии с положительным наклоном. Средние значения помогают избежать хаотичных выбросов, а также убрать влияние фактора сезонности из модели.

На основе расчетных уравнений линейной регрессии рассчитывается показатель R^2. Данный показатель объясняет то, как хорошо выбранное уравнение описывает реальные средние расходы. Если R^2 = 0,5, то это означает, что данное уравнение на 50% описывает взаимосвязь выбранных переменных (в нашем случае расхода (продаж) и времени). Рекомендуемое значение R^2 > 0.85.

Далее программа просит ввести нормативные значения R^2 отдельно для собственного расхода и продаж. На основе введенных значений выбирается последующая методология прогнозирования. Если уравнения регрессии показывают хорошую взаимосвязь расходов и времени (выше заданных нормативных значений R^2), тогда последующее прогнозирование будет сделано на основе уравнения регрессии, в противном случае будут браться заданные средние значения за определенный период времени, умноженный на соответствующий заданный коэффициент.

Стоит отметить, что уравнения линейной регрессии строятся для выявления закономерностей средних расходов (продаж), следовательно, на основе уравнения мы сможем спрогнозировать именно средний расход. Однако зная среднее значение для n месяцев и сумму n-1 предыдущих расходов можно узнать прогнозное значение расходов.

После прогнозирования расходов и продаж, рассчитываются помесячные остатки. Расчет помесячных остатков учитывает значение минимального остатка для собственного пр-ва (данное значение запрашивается программой). Если текущий остаток в прогнозируемом месяце больше заданного минимально остатка для собственного пр-ва, тогда в процессе расчете остатков учитываются продажи, в противном случае продажи учитываться не будут, а сумма продаж попадет в расчет кол-ва к заказу.

## 4. Подробное объяснение работы create_report
...


