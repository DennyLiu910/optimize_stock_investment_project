import yfinance as yf
import numpy as np
import scipy.optimize as sco
import json

# 從 Yahoo Finance 獲取股票價格
def get_stock_prices(tickers, period):
    data = yf.download(tickers, period=period)['Adj Close']
    data.columns = data.columns.str.upper()  # 確保股票代碼為大寫
    return data

# 優化投資組合
def optimize_portfolio(prices, strategy):
    # 計算每日收益率
    returns = prices.pct_change().dropna()
    # 計算平均收益率
    mean_returns = returns.mean()
    # 計算收益率協方差矩陣
    cov_matrix = returns.cov()

    # 投資組合方差
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))

    # 投資組合收益率
    def portfolio_return(weights):
        return np.dot(weights, mean_returns)

    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    # 約束條件：所有權重之和為1
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
    # 權重範圍：每個資產的權重在0到1之間
    bounds = tuple((0, 1) for _ in range(num_assets))
    # 初始猜測值：所有資產權重相等
    init_guess = num_assets * [1. / num_assets]

    # 根據策略設置風險迴避參數
    if strategy == 'conservative':
        risk_aversion = 10
    elif strategy == 'balanced':
        risk_aversion = 1
    else:  # aggressive
        risk_aversion = 0.1

    # 目標函數：風險迴避乘以投資組合方差減去投資組合收益率
    def objective(weights):
        return risk_aversion * portfolio_variance(weights) - portfolio_return(weights)

    # 使用SLSQP方法最小化目標函數
    result = sco.minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

# 主函數
def main():
    # 讀取輸入數據
    with open('portfolio_optimization_input.json', 'r') as f:
        input_data = json.load(f)

    investment_amount = input_data['investment_amount']
    tickers = [ticker.upper() for ticker in input_data['tickers']]  # 確保股票代碼為大寫
    strategy = input_data['strategy']
    period = input_data['period']

    # 獲取股票價格
    prices = get_stock_prices(tickers, period)
    # 優化投資組合
    optimal_weights = optimize_portfolio(prices, strategy)

    # 計算投資計劃
    investment_plan = {ticker: weight * investment_amount for ticker, weight in zip(tickers, optimal_weights)}
    # 計算年化預期回報率
    expected_return = np.sum(optimal_weights * prices.pct_change().mean()) * 252  # 年化收益率

    # 計算個別公司的預期獲利率和獲利金額
    individual_returns = {ticker: weight * prices.pct_change().mean()[ticker] * 252 for ticker, weight in zip(tickers, optimal_weights)}
    individual_profits = {ticker: investment_plan[ticker] * individual_returns[ticker] for ticker in tickers}

    # 結果
    result = {
        'investment_plan': investment_plan,
        'expected_return': expected_return,
        'individual_returns': individual_returns,
        'individual_profits': individual_profits
    }

    # 將結果寫入JSON文件
    with open('portfolio_optimization_result.json', 'w') as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()

