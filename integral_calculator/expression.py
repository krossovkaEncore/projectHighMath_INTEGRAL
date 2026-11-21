import csv

from pathlib import Path

from .integration import IntegrationResult


class ResultExporter:
    @staticmethod
    def export_csv(path: str | Path, result: IntegrationResult):
        with open(
            path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file, delimiter=";")

            writer.writerow(["Функция", result.expression])
            writer.writerow(["Нижняя граница", result.a])
            writer.writerow(["Верхняя граница", result.b])
            writer.writerow(["Количество разбиений", result.n])
            writer.writerow(["Метод", result.method.value])
            writer.writerow(["Шаг", result.step])
            writer.writerow(["Результат интегрирования", result.value])
            writer.writerow([])
            writer.writerow(["№", "x", "f(x)"])

            writer.writerows(result.table)

    @staticmethod
    def export_txt(path: str | Path, result: IntegrationResult):
        with open(path, "w", encoding="utf-8") as file:
            file.write("КАЛЬКУЛЯТОР ИНТЕГРАЛОВ\n")
            file.write("=" * 55 + "\n\n")

            file.write(f"Функция: {result.expression}\n")
            file.write(f"Границы: [{result.a}, {result.b}]\n")
            file.write(f"Разбиений: {result.n}\n")
            file.write(f"Метод: {result.method.value}\n")
            file.write(f"Шаг: {result.step:.10g}\n")
            file.write(f"Результат: {result.value:.12g}\n\n")

            file.write(
                f"{'№':<8}{'x':<22}{'f(x)':<22}\n"
            )
            file.write("-" * 52 + "\n")

            for index, x, fx in result.table:
                file.write(
                    f"{index:<8}{x:<22.10g}{fx:<22.10g}\n"
                )
