import sys
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QLabel, QMenuBar, QStackedWidget, QPushButton,
    QTableWidget, QGridLayout, QInputDialog, QMessageBox, QFormLayout,
    QGroupBox, QDoubleSpinBox)


class EconomicCurves(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Экономический калькулятор")
        self.setGeometry(100, 100, 1000, 800)
        self.setFixedSize(1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.demand_action = QAction("Кривая спроса", self)
        self.supply_action = QAction("Кривая предложения", self)
        self.info_action = QAction("КПД таблица", self)
        self.elast_action = QAction("Калькулятор эластичности", self)

        self.menu_bar.addAction(self.demand_action)
        self.menu_bar.addAction(self.supply_action)
        self.menu_bar.addAction(self.info_action)
        self.menu_bar.addAction(self.elast_action)

        self.demand_action.triggered.connect(self.show_demand_plot)
        self.supply_action.triggered.connect(self.show_supply_plot)
        self.info_action.triggered.connect(self.show_kpd_page)
        self.elast_action.triggered.connect(self.show_elast_page)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Страница спроса
        self.demand_page = QWidget()
        self.demand_layout = QVBoxLayout(self.demand_page)
        self.demand_price_input = QLineEdit()
        self.demand_quantity_input = QLineEdit()
        self.demand_plot_widget = pg.PlotWidget()
        self.demand_layout.addWidget(QLabel("Цена:"))
        self.demand_layout.addWidget(self.demand_price_input)
        self.demand_layout.addWidget(QLabel("Количество:"))
        self.demand_layout.addWidget(self.demand_quantity_input)
        self.demand_layout.addWidget(self.demand_plot_widget)
        self.stacked_widget.addWidget(self.demand_page)

        # Подключение графика
        self.demand_price_input.textChanged.connect(self.update_demand_graph)
        self.demand_quantity_input.textChanged.connect(self.update_demand_graph)

        # Страница предложения
        self.supply_page = QWidget()
        self.supply_layout = QVBoxLayout(self.supply_page)
        self.supply_price_input = QLineEdit()
        self.supply_quantity_input = QLineEdit()
        self.supply_plot_widget = pg.PlotWidget()
        self.supply_layout.addWidget(QLabel("Цена:"))
        self.supply_layout.addWidget(self.supply_price_input)
        self.supply_layout.addWidget(QLabel("Количество:"))
        self.supply_layout.addWidget(self.supply_quantity_input)
        self.supply_layout.addWidget(self.supply_plot_widget)
        self.stacked_widget.addWidget(self.supply_page)

        # Подключение графика
        self.supply_price_input.textChanged.connect(self.update_supply_graph)
        self.supply_quantity_input.textChanged.connect(self.update_supply_graph)

        # Страница кпд
        self.kpd_page = Ui_productivity_and_advantages()
        self.stacked_widget.addWidget(self.kpd_page)

        # Страница с калькулятором
        self.elast_page = ElasticityCalculator()
        self.stacked_widget.addWidget(self.elast_page)

        # Добавляем отслеживание изменений страницы
        self.stacked_widget.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        # Проверяем, является ли активная страница "калькулятором эластичности"
        if self.stacked_widget.widget(index) == self.elast_page:
            self.setGeometry(100, 100, 600, 800)  # Меняем параметры окна для калькулятора эластичности
            self.setFixedSize(600, 800)

        # Проверяем, является ли активная страница "КПД таблица"
        elif self.stacked_widget.widget(index) == self.kpd_page:
            self.setGeometry(100, 100, 800, 600)  # Меняем параметры окна для КПД таблицы
            self.setFixedSize(800, 600)

        else:
            self.setGeometry(100, 100, 1000, 800)  # Восстанавливаем начальные параметры окна
            self.setFixedSize(1000, 800)

    def show_demand_plot(self):
        self.stacked_widget.setCurrentWidget(self.demand_page)

    def show_supply_plot(self):
        self.stacked_widget.setCurrentWidget(self.supply_page)

    def show_kpd_page(self):
        self.stacked_widget.setCurrentWidget(self.kpd_page)

    def show_elast_page(self):
        self.stacked_widget.setCurrentWidget(self.elast_page)

    def update_demand_graph(self):
        price_text = self.demand_price_input.text()
        quantity_text = self.demand_quantity_input.text()

        if price_text:
            price = float(price_text)
        else:
            price = None

        if quantity_text:
            quantity = float(quantity_text)
        else:
            quantity = None

        if price is not None and quantity is not None:
            self.demand_plot_widget.clear()
            self.demand_plot_widget.plot([0, quantity], [price, 0])

    def update_supply_graph(self):
        price_text = self.supply_price_input.text()
        quantity_text = self.supply_quantity_input.text()

        if price_text:
            price = float(price_text)
        else:
            price = None

        if quantity_text:
            quantity = float(quantity_text)
        else:
            quantity = None

        if price is not None and quantity is not None:
            self.supply_plot_widget.clear()
            self.supply_plot_widget.plot([0, quantity], [0, price])


class Ui_productivity_and_advantages(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("productivity_and_advantages")
        self.resize(740, 578)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # кнопки и таблица
        self.proizv_add_btn = QPushButton("Добавить производителя", self)
        self.proizv_add_btn.clicked.connect(self.add_producer_dialog)
        self.gridLayout.addWidget(self.proizv_add_btn, 2, 0, 1, 1)

        self.remove_button = QPushButton("Удалить производителя", self)
        self.remove_button.clicked.connect(self.remove_producer_dialog)
        self.gridLayout.addWidget(self.remove_button, 3, 0, 1, 1)

        # Process button
        self.process_button = QPushButton("Обработать", self)
        self.process_button.clicked.connect(self.process_data)
        self.gridLayout.addWidget(self.process_button, 4, 0, 1, 1)  # Place it below other buttons

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(4)  # Only Q, TC, t, and P columns
        self.tableWidget.setRowCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Q", "TC", "t", "P"])
        self.tableWidget.setVerticalHeaderLabels(["Производитель 1", "Производитель 2"])
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

        for row in range(self.tableWidget.rowCount()):
            default_t_item = QtWidgets.QTableWidgetItem("1")  # Default value for 't'
            self.tableWidget.setItem(row, 2, default_t_item)

        self.absolute_advantage_label = QLabel("Абсолютное преимущество имеет: ", self)
        self.gridLayout.addWidget(self.absolute_advantage_label, 5, 0, 1, 1)

    def add_producer_dialog(self):
        producer_name, ok = QInputDialog.getText(self, "Добавить производителя", "Введите название производителя:")
        if ok and producer_name:
            current_row_count = self.tableWidget.rowCount()
            if current_row_count < 10:  # Example limit, can be adjusted
                self.tableWidget.insertRow(current_row_count)  # Add a new row
                default_t_item = QtWidgets.QTableWidgetItem("1")  # Default t value
                self.tableWidget.setItem(current_row_count, 2, default_t_item)
                self.tableWidget.setVerticalHeaderItem(current_row_count, QtWidgets.QTableWidgetItem(producer_name))
            else:
                QMessageBox.warning(self, "Ошибка", "Достигнуто максимальное количество производителей.")

    def remove_producer_dialog(self):
        producer_name, ok = QInputDialog.getText(self, "Удалить производителя", "Введите название производителя для удаления:")
        if ok and producer_name:
            current_row = self.find_producer_row(producer_name)
            if current_row != -1:
                self.tableWidget.removeRow(current_row)  # Remove the selected row
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
                # Fetch values from the table
                Q_item = self.tableWidget.item(row, 0)
                Q_text = Q_item.text() if Q_item else ''
                Q = float(Q_text) if Q_text else None

                TC_item = self.tableWidget.item(row, 1)
                TC_text = TC_item.text() if TC_item else ''
                TC = float(TC_text) if TC_text else None

                t_item = self.tableWidget.item(row, 2)
                t_text = t_item.text() if t_item else '1'
                t = float(t_text) if t_text else 1  # Default t to 1 if not provided

                P_item = self.tableWidget.item(row, 3)
                P_text = P_item.text() if P_item else ''
                P = float(P_text) if P_text else None

                # Validate input
                if Q is not None and Q <= 0 and (P is not None and P > 0):
                    QMessageBox.warning(self, "Ошибка", "Некорректный ввод: Q не может быть меньше или равно нулю, если P больше нуля.")
                    return

                if TC is not None and TC < 0:
                    QMessageBox.warning(self, "Ошибка", "Некорректный ввод: TC не может быть отрицательным.")
                    return

                # Calculate missing value
                if Q is not None and TC is not None and t > 0:  # Q, TC, t are known, calculate P
                    P = Q / (TC * t)
                    P_item = QtWidgets.QTableWidgetItem(f"{P:.2f}")
                    self.tableWidget.setItem(row, 3, P_item)
                elif Q is not None and TC is not None and P is not None:  # Q, TC, P are known, calculate t
                    t = TC / (Q / P)
                    t_item = QtWidgets.QTableWidgetItem(f"{t:.2f}")
                    self.tableWidget.setItem(row, 2, t_item)
                elif Q is not None and P is not None and t > 0:  # Q, P, t are known, calculate TC
                    TC = Q / P * t
                    TC_item = QtWidgets.QTableWidgetItem(f"{TC:.2f}")
                    self.tableWidget.setItem(row, 1, TC_item)
                elif TC is not None and P is not None and t > 0:  # TC, P, t are known, calculate Q
                    Q = TC * P / t
                    Q_item = QtWidgets.QTableWidgetItem(f"{Q:.2f}")
                    self.tableWidget.setItem(row, 0, Q_item)

            self.calculate_absolute_advantage()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректный ввод: Пожалуйста, проверьте введенные значения.")

    def calculate_absolute_advantage(self):
        max_productivity = -1
        producer_name = ""
        for row in range(self.tableWidget.rowCount()):
            P_item = self.tableWidget.item(row, 3)
            P_text = P_item.text() if P_item else '0'
            P = float(P_text) if P_text else 0
            if P > max_productivity:
                max_productivity = P
                header_item = self.tableWidget.verticalHeaderItem(row)
                producer_name = header_item.text() if header_item else ""
        self.absolute_advantage_label.setText(f"Абсолютное преимущество имеет: {producer_name}")


class ElasticityCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Эластичность калькулятор")
        self.setFixedSize(600, 800)  # фиксированный размер окна
        self.initUI()
        self.setGeometry(100, 100, 600, 800)
        self.setFixedSize(600, 800)

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

        try:
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
                elasticity_price = "Ошибка: сумма начального и конечного значения\nцены или количества не должна быть равна 0"

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

        except ZeroDivisionError:
            self.result_label.setText("Ошибка: деление на ноль. Проверьте входные данные.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EconomicCurves()
    window.show()
    sys.exit(app.exec())