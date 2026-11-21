import tkinter as tk

from integral_calculator.gui import IntegralCalculatorApp


def main():
    root = tk.Tk()
    IntegralCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
