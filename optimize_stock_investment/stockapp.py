import os
import sys
import json
import flet as ft
from analysis import analyze_portfolio

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main(page: ft.Page):
    page.title = "股票投資組合最佳化"
    page.window_width = 1000
    page.window_height = 600
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def analyze_click(e):
        if not investment_amount_input.value or not num_companies_input.value:
            result_text.value = "請輸入完整資訊。"
            result_text.visible = True
            page.update()
            return

        try:
            investment_amount = float(investment_amount_input.value)
        except ValueError:
            result_text.value = "請輸入有效的投資金額。"
            result_text.visible = True
            page.update()
            return

        try:
            num_companies = min(int(num_companies_input.value), 6)
        except ValueError:
            result_text.value = "請輸入有效的公司數量。"
            result_text.visible = True
            page.update()
            return

        tickers = [ticker_input.value.strip().upper() for ticker_input in ticker_inputs[:num_companies]]
        if not all(tickers):
            result_text.value = "請輸入所有公司的股票代碼。"
            result_text.visible = True
            page.update()
            return

        strategy = strategy_dropdown.value
        period = period_dropdown.value
        result_text.value = " "

        result = analyze_portfolio(investment_amount, tickers, strategy, period)

        if 'error' in result:
            result_text.value = result['error']
        else:
            investment_plan = result['investment_plan']
            expected_return = result['expected_return']
            individual_returns = result['individual_returns']

            rows = []
            current_row = []
            for i, (ticker, amount) in enumerate(investment_plan.items()):
                investment_info = ft.Column([
                    ft.Text(f"公司: {ticker}"),
                    ft.Text(f"投資金額: {amount:.2f} NTD"),
                    ft.Text(f"預期獲利率: {individual_returns[ticker]:.2%}"),
                    ft.Text(f"預期獲利金額: {individual_returns[ticker] * amount:.2f} NTD")
                ], spacing=5)

                current_row.append(investment_info)

                if (i + 1) % 3 == 0 or (i + 1) == len(investment_plan):
                    rows.append(ft.Row(current_row, alignment=ft.MainAxisAlignment.CENTER, spacing=20))
                    current_row = []

            result_container.controls = [
                ft.Row([ft.Text(f"預期回報率: {expected_return:.2%}")], alignment=ft.MainAxisAlignment.CENTER),  # 置中顯示
                *rows
            ]

        result_container.visible = True
        page.update()

    def num_companies_change(e):
        try:
            num_companies = int(num_companies_input.value)
            num_companies = min(num_companies, 6)
        except ValueError:
            return

        ticker_inputs.clear()
        ticker_container.controls.clear()

        rows = []
        for i in range(num_companies):
            if i % 3 == 0:
                row = ft.Row([], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                rows.append(row)

            ticker_input = ft.TextField(label=f"公司 {i + 1} 股票代碼", width=200)
            ticker_inputs.append(ticker_input)
            rows[-1].controls.append(ticker_input)

        for row in rows:
            ticker_container.controls.append(row)

        page.update()

    investment_amount_input = ft.TextField(label="投資金額（NTD）", width=200)
    num_companies_input = ft.TextField(label="想投資的標的個數", width=200, on_change=num_companies_change)
    strategy_dropdown = ft.Dropdown(
        label="投資策略",
        options=[
            ft.dropdown.Option(key="conservative", text="保守型"),
            ft.dropdown.Option(key="balanced", text="穩健型"),
            ft.dropdown.Option(key="aggressive", text="積極型")
        ],
        width=200
    )
    period_dropdown = ft.Dropdown(
        label="投資期間",
        options=[
            ft.dropdown.Option(key="1mo", text="短期（一個月）"),
            ft.dropdown.Option(key="6mo", text="中期（六個月）"),
            ft.dropdown.Option(key="1y", text="長期（一年）")
        ],
        width=200
    )
    analyze_button = ft.ElevatedButton(text="分析投資報酬率", width=200, on_click=analyze_click)
    result_text = ft.Text(visible=False)
    result_container = ft.Column(visible=False)

    ticker_inputs = []
    ticker_container = ft.Column(spacing=20)  # 垂直間隔

    page.add(
        ft.Column([
            ft.Row([investment_amount_input, num_companies_input], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Row([strategy_dropdown, period_dropdown], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Row([analyze_button], alignment=ft.MainAxisAlignment.CENTER),
            ticker_container,
            result_container,
            ft.Row([result_text], alignment=ft.MainAxisAlignment.CENTER)  # 將提示文字置中
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    )

ft.app(target=main)
