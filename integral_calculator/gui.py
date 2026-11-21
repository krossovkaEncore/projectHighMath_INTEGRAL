import tkinter as tk

from tkinter import ttk, filedialog, messagebox

from .expression import SafeExpression
from .integration import IntegrationMethod, NumericalIntegrator
from .exporters import ResultExporter


class IntegralCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Калькулятор интегралов")
        self.root.geometry("950x650")
        self.root.minsize(750, 500)

        self.result = None

        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(
            main,
            text="Параметры интегрирования",
            padding=10
        )
        input_frame.pack(fill=tk.X)

        self.function_entry = self.create_entry(
            input_frame, "Функция f(x):", "x**2 + 2*x + 1", 0
        )

        self.a_entry = self.create_entry(
            input_frame, "Нижняя граница a:", "0", 1
        )

        self.b_entry = self.create_entry(
            input_frame, "Верхняя граница b:", "5", 2
        )

        self.n_entry = self.create_entry(
            input_frame, "Количество разбиений N:", "100", 3
        )

        ttk.Label(
            input_frame,
            text="Метод интегрирования:"
        ).grid(row=4, column=0, sticky="w", padx=5, pady=5)

        self.method_box = ttk.Combobox(
            input_frame,
            values=[method.value for method in IntegrationMethod],
            state="readonly",
            width=30
        )
        self.method_box.current(0)
        self.method_box.grid(
            row=4, column=1, sticky="w", padx=5, pady=5
        )

        input_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(main)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Вычислить",
            command=self.calculate
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Экспорт CSV",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Экспорт TXT",
            command=self.export_txt
        ).pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(
            main,
            text="Результат",
            padding=10
        )
        result_frame.pack(fill=tk.X)

        self.result_label = ttk.Label(
            result_frame,
            text="Ожидание вычислений...",
            font=("Segoe UI", 12, "bold")
        )
        self.result_label.pack(anchor="w")

        table_frame = ttk.LabelFrame(
            main,
            text="Таблица значений функции",
            padding=5
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("index", "x", "fx")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.table.heading("index", text="№")
        self.table.heading("x", text="x")
        self.table.heading("fx", text="f(x)")

        self.table.column("index", width=70, anchor="center")
        self.table.column("x", width=200, anchor="center")
        self.table.column("fx", width=300, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview
        )

        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    @staticmethod
    def create_entry(parent, label, default, row):
        ttk.Label(
            parent,
            text=label
        ).grid(row=row, column=0, sticky="w", padx=5, pady=5)

        entry = ttk.Entry(parent, width=35)
        entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        return entry

    def calculate(self):
        try:
            expression = self.function_entry.get()
            function = SafeExpression(expression)

            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            n = int(self.n_entry.get())

            method = next(
                method
                for method in IntegrationMethod
                if method.value == self.method_box.get()
            )

            result = NumericalIntegrator.integrate(
                function=function,
                a=a,
                b=b,
                n=n,
                method=method,
                expression=expression
            )

            self.result = result
            self.update_table(result)

            self.result_label.config(
                text=(
                    f"Метод: {result.method.value} | "
                    f"Интеграл: {result.value:.12g} | "
                    f"Шаг: {result.step:.8g}"
                )
            )

        except (ValueError, TypeError, ArithmeticError, OverflowError) as error:
            messagebox.showerror("Ошибка вычисления", str(error))

        except Exception as error:
            messagebox.showerror(
                "Неожиданная ошибка",
                f"Не удалось выполнить вычисление: {error}"
            )

    def update_table(self, result):
        self.table.delete(*self.table.get_children())

        for index, x, fx in result.table:
            self.table.insert(
                "",
                tk.END,
                values=(
                    index,
                    f"{x:.8g}",
                    f"{fx:.10g}"
                )
            )

    def export_csv(self):
        self.export_result("csv")

    def export_txt(self):
        self.export_result("txt")

    def export_result(self, format_name):
        if self.result is None:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала выполните вычисления."
            )
            return

        extension = f".{format_name}"

        path = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[
                (f"{format_name.upper()} файлы", f"*{extension}")
            ]
        )

        if not path:
            return

        try:
            if format_name == "csv":
                ResultExporter.export_csv(path, self.result)
            else:
                ResultExporter.export_txt(path, self.result)

            messagebox.showinfo(
                "Экспорт",
                "Результаты успешно сохранены."
            )

        except OSError as error:
            messagebox.showerror(
                "Ошибка сохранения",
                str(error)
            )
