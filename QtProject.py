import sys
import sqlite3
import pyqtgraph as pg
from PyQt6 import QtCore
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QLabel, QMenuBar, QStackedWidget, QPushButton,
    QTableWidget, QGridLayout, QInputDialog, QMessageBox, QFormLayout,
    QGroupBox, QDoubleSpinBox, QTableWidgetItem)


class EconomicCurves(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Экономический калькулятор")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.demandSupply_action = QAction("Кривая спроса и предложения", self)
        self.info_action = QAction("КПД таблица", self)
        self.elast_action = QAction("Калькулятор эластичности", self)

        self.menu_bar.addAction(self.demandSupply_action)
        self.menu_bar.addAction(self.info_action)
        self.menu_bar.addAction(self.elast_action)

        self.demandSupply_action.triggered.connect(self.show_demandSupply_plot)
        self.info_action.triggered.connect(self.show_kpd_page)
        self.elast_action.triggered.connect(self.show_elast_page)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Страница спроса и предложения
        self.demandSupply_page = QWidget()
        self.demandSupply_layout = QVBoxLayout(self.demandSupply_page)
        self.demandSupply_price_input = QLineEdit()
        self.demandSupply_quantity_input = QLineEdit()
        self.demandSupply_plot_widget = pg.PlotWidget()

        # Добавляем метки к осям графика
        self.demandSupply_plot_widget.setLabel('left', 'Цена')
        self.demandSupply_plot_widget.setLabel('bottom', 'Количество')

        self.demandSupply_layout.addWidget(QLabel("Цена:"))
        self.demandSupply_layout.addWidget(self.demandSupply_price_input)
        self.demandSupply_layout.addWidget(QLabel("Количество:"))
        self.demandSupply_layout.addWidget(self.demandSupply_quantity_input)
        self.demandSupply_layout.addWidget(self.demandSupply_plot_widget)
        self.stacked_widget.addWidget(self.demandSupply_page)

        # Подключение графика
        self.demandSupply_price_input.textChanged.connect(self.update_demandSupply_graph)
        self.demandSupply_quantity_input.textChanged.connect(self.update_demandSupply_graph)

        # Страница кпд
        self.kpd_page = Ui_productivity_and_advantages()
        self.stacked_widget.addWidget(self.kpd_page)

        # Страница с калькулятором
        self.elast_page = ElasticityCalculator()
        self.stacked_widget.addWidget(self.elast_page)

        # Добавляем отслеживание изменений страницы
        self.stacked_widget.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        current_widget = self.stacked_widget.widget(index)

        # Получаем размеры текущего виджета
        if current_widget == self.elast_page:
            new_width, new_height = 600, 800
        elif current_widget == self.kpd_page:
            new_width, new_height = 740, 578  # Используем размер, который вы указали в Ui_productivity_and_advantages
        else:
            new_width, new_height = 1000, 800

        # Изменяем размер окна с учётом этих данных
        self.resize(new_width, new_height)

    def show_demandSupply_plot(self):
        self.stacked_widget.setCurrentWidget(self.demandSupply_page)

    def show_kpd_page(self):
        self.stacked_widget.setCurrentWidget(self.kpd_page)

    def show_elast_page(self):
        self.stacked_widget.setCurrentWidget(self.elast_page)

    def update_demandSupply_graph(self):
        price_text = self.demandSupply_price_input.text()
        quantity_text = self.demandSupply_quantity_input.text()

        if price_text:
            price = float(price_text)
        else:
            price = None

        if quantity_text:
            quantity = float(quantity_text)
        else:
            quantity = None

        if price is not None and quantity is not None:
            self.demandSupply_plot_widget.clear()

            # Кривая спроса
            self.demandSupply_plot_widget.plot([0, quantity], [price, 0], pen='r', name="Кривая спроса")

            # Кривая предложения
            self.demandSupply_plot_widget.plot([0, quantity], [0, price], pen='g', name="Кривая предложения")


class Ui_productivity_and_advantages(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("productivity_and_advantages")
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # кнопки и таблица
        self.proizv_add_btn = QPushButton("Добавить производителя", self)
        self.proizv_add_btn.clicked.connect(self.add_producer_dialog)
        self.gridLayout.addWidget(self.proizv_add_btn, 2, 0, 1, 1)

        self.remove_button = QPushButton("Удалить производителя", self)
        self.remove_button.clicked.connect(self.remove_producer_dialog)
        self.gridLayout.addWidget(self.remove_button, 3, 0, 1, 1)

        self.save_button = QPushButton("Сохранить данные", self)
        self.save_button.clicked.connect(self.save_result)
        self.gridLayout.addWidget(self.save_button, 6, 0, 1, 1)

        # Кнопка обработки
        self.process_button = QPushButton("Обработать", self)
        self.process_button.clicked.connect(self.process_data)
        self.gridLayout.addWidget(self.process_button, 4, 0, 1, 1)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Q", "Q2", "TC", "t", "P", "P2"])
        self.tableWidget.setVerticalHeaderLabels(["Производитель 1", "Производитель 2"])
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

        # Устанавливаем подсказки для каждого столбца
        self.set_column_tooltips()

        self.producer_name = ''
        self.relative_advantage = ''

        for row in range(self.tableWidget.rowCount()):
            default_t_item = QTableWidgetItem("1.00")  # значение по умолчанию  для 't'
            self.tableWidget.setItem(row, 3, default_t_item)

        self.absolute_advantage_label = QLabel(f"Абсолютное преимущество имеет: {self.producer_name}"
                                               f" \nОтносительное преимущество имеет: {self.relative_advantage}", self)
        self.gridLayout.addWidget(self.absolute_advantage_label, 5, 0, 1, 1)

    def set_column_tooltips(self):  # метод по созданию подсказок

        tooltips = {
            "Q": "Количество произведенного товара",
            "Q2": "Количество второго товара, произведенного вместо первого",
            "TC": "Общие затраты (Total Cost)",
            "t": "Время на производство единицы товара",
            "P": "Производительность (Q / (TC * t))",
            "P2": "Производительность для второго товара (Q2 / (TC * t))",
        }

        for col_index, header_name in enumerate(tooltips.keys()):
            header_item = self.tableWidget.horizontalHeaderItem(col_index)
            header_item.setToolTip(tooltips[header_name])  # Устанавливаем подсказку для заголовка столбца

    def add_producer_dialog(self):  # функция добавления производителя
        producer_name, ok = QInputDialog.getText(self, "Добавить производителя", "Введите название производителя:")
        if ok and producer_name:
            current_row_count = self.tableWidget.rowCount()
            if current_row_count < 100:
                self.tableWidget.insertRow(current_row_count)  # добавляем новую строку(запись)
                default_t_item = QTableWidgetItem("1")
                self.tableWidget.setItem(current_row_count, 3, default_t_item)
                self.tableWidget.setVerticalHeaderItem(current_row_count, QTableWidgetItem(producer_name))
            else:
                QMessageBox.warning(self, "Ошибка", "Достигнуто максимальное количество производителей.")

    def remove_producer_dialog(self):  # функция удаления производителя
        producer_name, ok = QInputDialog.getText(self, "Удалить производителя",
                                                 "Введите название производителя для удаления:")
        if ok and producer_name:
            current_row = self.find_producer_row(producer_name)
            if current_row != -1:
                self.tableWidget.removeRow(current_row)  # Удаляем выбранную строку
            else:
                QMessageBox.warning(self, "Ошибка", "Производитель не найден.")

    def find_producer_row(self, producer_name):
        for row in range(self.tableWidget.rowCount()):
            header_item = self.tableWidget.verticalHeaderItem(row)
            if header_item and header_item.text() == producer_name:
                return row
        return -1  # Not found

    def process_data(self):
        try:
            for row in range(self.tableWidget.rowCount()):
                # Получение Q
                Q_item = self.tableWidget.item(row, 0)
                if Q_item and Q_item.text():
                    Q = float(Q_item.text())
                else:
                    Q = None

                # Получение Q2
                Q2_item = self.tableWidget.item(row, 1)
                if Q2_item and Q2_item.text():
                    Q2 = float(Q2_item.text())
                else:
                    Q2 = None

                # Получение TC
                TC_item = self.tableWidget.item(row, 2)
                if TC_item and TC_item.text():
                    TC = float(TC_item.text())
                else:
                    TC = None

                # Получение t
                t_item = self.tableWidget.item(row, 3)
                if t_item and t_item.text():
                    t = float(t_item.text())
                else:
                    t = 1.00  # Значение по умолчанию - 1

                # Получение P
                P_item = self.tableWidget.item(row, 4)
                if P_item and P_item.text():
                    P = float(P_item.text())
                else:
                    P = None

                # Получение P2
                P2_item = self.tableWidget.item(row, 5)
                if P2_item and P2_item.text():
                    P2 = float(P2_item.text())
                else:
                    P2 = None

                # Вычисление недостающего значения для Q, TC, P, t
                if Q is not None and TC is not None and t > 0:
                    P = Q / (TC * t)
                    P_item = QTableWidgetItem(f"{P:.2f}")
                    self.tableWidget.setItem(row, 4, P_item)
                elif Q is not None and TC is not None and P is not None:
                    t = TC / (Q / P)
                    t_item = QTableWidgetItem(f"{t:.2f}")
                    self.tableWidget.setItem(row, 3, t_item)
                elif Q is not None and P is not None and t > 0:
                    TC = Q / P * t
                    TC_item = QTableWidgetItem(f"{TC:.2f}")
                    self.tableWidget.setItem(row, 2, TC_item)
                elif TC is not None and P is not None and t > 0:
                    Q = TC * P / t
                    Q_item = QTableWidgetItem(f"{Q:.2f}")
                    self.tableWidget.setItem(row, 0, Q_item)

                # Вычисление недостающего значения для Q2, P2, TC, t
                if Q2 is not None and TC is not None and t > 0:
                    P2 = Q2 / (TC * t)
                    P2_item = QTableWidgetItem(f"{P2:.2f}")
                    self.tableWidget.setItem(row, 5, P2_item)
                elif Q2 is not None and TC is not None and P2 is not None:
                    t = TC / (Q2 / P2)
                    t_item = QTableWidgetItem(f"{t:.2f}")
                    self.tableWidget.setItem(row, 3, t_item)
                elif Q2 is not None and P2 is not None and t > 0:
                    TC = Q2 / P2 * t
                    TC_item = QTableWidgetItem(f"{TC:.2f}")
                    self.tableWidget.setItem(row, 2, TC_item)
                elif TC is not None and P2 is not None and t > 0:
                    Q2 = TC * P2 / t
                    Q2_item = QTableWidgetItem(f"{Q2:.2f}")
                    self.tableWidget.setItem(row, 1, Q2_item)

            self.update_advantages_result()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректный ввод: Пожалуйста, проверьте введенные значения.")

    def calculate_absolute_advantage(self):  # функция определения абсолютного преимщуества (чьё P1 больше)
        max_productivity = -1
        producer_name = ""
        for row in range(self.tableWidget.rowCount()):
            P_item = self.tableWidget.item(row, 4)
            if P_item and P_item.text():
                P = float(P_item.text())
            else:
                P = 0
            if P > max_productivity:
                max_productivity = P
                header_item = self.tableWidget.verticalHeaderItem(row)
                if header_item:
                    producer_name = header_item.text()
                else:
                    producer_name = ""
        self.producer_name = producer_name

    def calculate_relative_advantage(self):
        min_opportunity_cost = float('inf')  # Минимальная альтернативная стоимость
        relative_advantage_producer = ""

        for row in range(self.tableWidget.rowCount()):
            Q_item = self.tableWidget.item(row, 0)
            Q2_item = self.tableWidget.item(row, 1)

            # Проверяем, что оба значения Q и Q2 заданы
            if Q_item and Q_item.text() and Q2_item and Q2_item.text():
                try:
                    Q = float(Q_item.text())
                    Q2 = float(Q2_item.text())

                    if Q2 > 0:  # Избегаем деления на 0
                        opportunity_cost = Q / Q2
                        if opportunity_cost < min_opportunity_cost:
                            min_opportunity_cost = opportunity_cost
                            header_item = self.tableWidget.verticalHeaderItem(row)
                            relative_advantage_producer = header_item.text() if header_item else ""
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Некорректный ввод: Пожалуйста, проверьте значения Q и Q2.")
                    return

        # Обновляем метку с результатом
        if relative_advantage_producer:
            self.relative_advantage = relative_advantage_producer
        else:
            self.relative_advantage = "Относительное преимущество определить не удалось."

    def update_advantages_result(self):
        self.calculate_absolute_advantage()
        self.calculate_relative_advantage()
        self.absolute_advantage_label.setText(
            f"Абсолютное преимущество имеет: {self.producer_name}\n"
            f"Относительное преимущество имеет: {self.relative_advantage}"
        )

    def get_table_data(self, table_widget):
        rows = table_widget.rowCount()
        columns = table_widget.columnCount()
        data = []

        for row in range(rows):
            row_data = []
            for col in range(columns):
                item = table_widget.item(row, col)
                row_data.append(item.text() if item else "")  # Если ячейка пустая, записываем пустую строку
            data.append(row_data)
        return data

    def save_result(self):
        try:
            # Подключаемся к SQLite базе данных
            conn = sqlite3.connect('result.sqlite')  # Создаем файл
            cursor = conn.cursor()

            # Формируем SQL-запрос для создания таблицы
            column_names = ["Q", "Q2", "TC", "t", "P", "P2"]
            columns_definition = ", ".join([f"{col} TEXT" for col in column_names])
            create_table_query = f"CREATE TABLE IF NOT EXISTS producers ({columns_definition})"
            cursor.execute(create_table_query)

            # Получаем данные из таблицы
            data = self.get_table_data(self.tableWidget)

            # Формируем строку с плейсхолдерами для значений
            placeholders = ", ".join(["?"] * len(column_names))
            insert_query = f"INSERT INTO producers VALUES ({placeholders})"

            # Вставляем данные построчно
            for row in data:
                cursor.execute(insert_query, row)

            conn.commit()  # Сохраняем изменения
            conn.close()  # Закрываем соединение

            # Сообщение об успешном сохранении
            QMessageBox.information(self, "Успех", "Данные успешно сохранены в базу данных!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении: {e}")


class ElasticityCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Эластичность калькулятор")
        self.initUI()
        self.setGeometry(100, 100, 600, 800)

    def initUI(self):
        main_layout = QVBoxLayout()

        # Группа для эластичности замещения ресурсов
        substitution_group = QGroupBox("Эластичность замещения ресурсов")
        substitution_layout = QFormLayout()

        # Поля для ввода значений K, L, P1 и Pr
        self.capital_input = QDoubleSpinBox()
        self.capital_input.setPrefix("K = ")
        self.capital_input.setRange(0, 1e6)  # Ограничения по значению для удобства

        self.labor_input = QDoubleSpinBox()
        self.labor_input.setPrefix("L = ")
        self.labor_input.setRange(0, 1e6)

        self.wage_price_input = QDoubleSpinBox()
        self.wage_price_input.setPrefix("P1 = ")
        self.wage_price_input.setRange(0, 1e6)

        self.capital_price_input = QDoubleSpinBox()
        self.capital_price_input.setPrefix("Pr = ")
        self.capital_price_input.setRange(0, 1e6)

        substitution_layout.addRow("Капитал (K):", self.capital_input)
        substitution_layout.addRow("Труд (L):", self.labor_input)
        substitution_layout.addRow("Цена труда (P1):", self.wage_price_input)
        substitution_layout.addRow("Цена капитала (Pr):", self.capital_price_input)
        substitution_group.setLayout(substitution_layout)
        main_layout.addWidget(substitution_group)

        # Группа для эластичности спроса по цене
        demand_group = QGroupBox("Эластичность спроса по цене")
        demand_layout = QFormLayout()

        self.demand_initial_price = QDoubleSpinBox()
        self.demand_final_price = QDoubleSpinBox()
        self.demand_initial_quantity = QDoubleSpinBox()
        self.demand_final_quantity = QDoubleSpinBox()

        demand_layout.addRow("Прежнея цена (p1):", self.demand_initial_price)
        demand_layout.addRow("Новая цена цена (p2):", self.demand_final_price)
        demand_layout.addRow("Величина спроса \nпри прежней цене (q1):", self.demand_initial_quantity)
        demand_layout.addRow("Величина спроса \nпри новой цене (q2):", self.demand_final_quantity)
        demand_group.setLayout(demand_layout)
        main_layout.addWidget(demand_group)

        # Группа для коэффициента перекрестной эластичности спроса
        cross_group = QGroupBox("Коэффициент перекрестной эластичности спроса")
        cross_layout = QFormLayout()

        self.cross_initial_price_x = QDoubleSpinBox()
        self.cross_final_price_x = QDoubleSpinBox()
        self.cross_initial_quantity_y = QDoubleSpinBox()
        self.cross_final_quantity_y = QDoubleSpinBox()

        cross_layout.addRow("Начальная цена товара X:", self.cross_initial_price_x)
        cross_layout.addRow("Конечная цена товара X:", self.cross_final_price_x)
        cross_layout.addRow("Начальное количество товара Y:", self.cross_initial_quantity_y)
        cross_layout.addRow("Конечное количество товара Y:", self.cross_final_quantity_y)
        cross_group.setLayout(cross_layout)
        main_layout.addWidget(cross_group)

        # Кнопка для расчета
        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.clicked.connect(self.calculate_elasticities)
        main_layout.addWidget(self.calculate_button)

        # Лейбл для вывода результатов
        self.result_label = QLabel("Результат будет показан здесь")
        self.result_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.result_label)

        # Установка основного макета
        self.setLayout(main_layout)

    def calculate_elasticities(self):
        # Получаем значения для эластичности замещения ресурсов
        K = self.capital_input.value()
        L = self.labor_input.value()
        P1 = self.wage_price_input.value()
        Pr = self.capital_price_input.value()

        # Получаем значения для расчета эластичности спроса по цене
        p_initial = self.demand_initial_price.value()
        p_final = self.demand_final_price.value()
        q_initial = self.demand_initial_quantity.value()
        q_final = self.demand_final_quantity.value()

        # Получаем значения для расчета коэффициента перекрестной эластичности спроса
        px_initial = self.cross_initial_price_x.value()
        px_final = self.cross_final_price_x.value()
        qy_initial = self.cross_initial_quantity_y.value()
        qy_final = self.cross_final_quantity_y.value()

        # Расчет эластичности замещения ресурсов
        if L != 0 and Pr != 0:
            capital_labor_ratio = K / L
            price_ratio = P1 / Pr
            elasticity_substitution = round((capital_labor_ratio / price_ratio), 3)
        else:
            elasticity_substitution = "Ошибка: L и Pr должны быть больше 0"

        # Расчет эластичности спроса по цене
        if q_initial + q_final != 0 and p_initial + p_final != 0:
            elasticity_price = round((((q_final - q_initial) / (q_initial + q_final)) / (
                (p_final - p_initial) / (p_initial + p_final))), 3)
        else:
            elasticity_price = ("Ошибка: сумма начального и конечного значения\n"
                                "цены или количества не должна быть равна 0")

        # Расчет перекрестной эластичности спроса
        if qy_initial != 0 and px_initial != 0:
            delta_qy = qy_final - qy_initial
            delta_px = px_final - px_initial
            elasticity_cross = round(((delta_qy / qy_initial) / (delta_px / px_initial)), 3)
        else:
            elasticity_cross = "Ошибка: начальные значения\nспроса или цены не должны быть равны 0"

        # Выводим результаты в лейбл
        self.result_label.setText(
            f"Эластичность замещения: {elasticity_substitution}\n"
            "\n"
            f"Эластичность спроса по цене: {elasticity_price}\n"
            "\n"
            f"Перекрестная эластичность: {elasticity_cross}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EconomicCurves()
    window.show()
    sys.exit(app.exec())


# created by Поджарых Сергей
