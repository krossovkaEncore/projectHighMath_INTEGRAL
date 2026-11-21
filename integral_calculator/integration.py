import math

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class IntegrationMethod(Enum):
    LEFT = "Левые прямоугольники"
    RIGHT = "Правые прямоугольники"
    MIDDLE = "Средние прямоугольники"
    TRAPEZOID = "Метод трапеций"


@dataclass(frozen=True)
class IntegrationResult:
    expression: str
    a: float
    b: float
    n: int
    method: IntegrationMethod
    step: float
    value: float
    table: tuple[tuple[int, float, float], ...]


class NumericalIntegrator:
    MAX_INTERVALS = 5000

    @staticmethod
    def integrate(
        function: Callable[[float], float],
        a: float,
        b: float,
        n: int,
        method: IntegrationMethod,
        expression: str = "",
    ) -> IntegrationResult:

        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("Границы должны быть конечными числами.")

        if b <= a:
            raise ValueError("Граница b должна быть больше a.")

        if not 1 <= n <= NumericalIntegrator.MAX_INTERVALS:
            raise ValueError(
                f"Количество разбиений должно быть от 1 до "
                f"{NumericalIntegrator.MAX_INTERVALS}."
            )

        step = (b - a) / n

        if not math.isfinite(step) or step <= 0:
            raise ValueError("Некорректный шаг интегрирования.")

        if method == IntegrationMethod.LEFT:
            points = (
                a + i * step
                for i in range(n)
            )
            value = step * math.fsum(function(x) for x in points)

        elif method == IntegrationMethod.RIGHT:
            points = (
                a + (i + 1) * step
                for i in range(n)
            )
            value = step * math.fsum(function(x) for x in points)

        elif method == IntegrationMethod.MIDDLE:
            points = (
                a + (i + 0.5) * step
                for i in range(n)
            )
            value = step * math.fsum(function(x) for x in points)

        elif method == IntegrationMethod.TRAPEZOID:
            inner_points = (
                a + i * step
                for i in range(1, n)
            )

            value = step * (
                (function(a) + function(b)) / 2
                + math.fsum(function(x) for x in inner_points)
            )

        else:
            raise ValueError("Неизвестный метод интегрирования.")

        if not math.isfinite(value):
            raise ValueError("Результат интегрирования не является конечным числом.")

        table = tuple(
            (i, a + i * step, function(a + i * step))
            for i in range(n + 1)
        )

        return IntegrationResult(
            expression=expression,
            a=a,
            b=b,
            n=n,
            method=method,
            step=step,
            value=value,
            table=table,
        )
