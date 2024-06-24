import yfinance as yf
import numpy as np
import scipy.optimize as sco

def get_stock_prices(tickers, period):
    """
    下載指定股票代碼在指定期間的調整後收盤價。
    
    :param tickers: 股票代碼列表
    :param period: 資料下載期間
    :return: 股票調整後收盤價的DataFrame
    """
    data = yf.download(tickers, period=period)['Adj Close']
    data.columns = data.columns.str.upper()  # 確保股票代碼為大寫
    return data

def optimize_portfolio(prices, strategy):
    """
    根據給定的投資策略，對股票投資組合進行優化。
    
    :param prices: 股票價格的DataFrame
    :param strategy: 投資策略（'conservative', 'balanced', 'aggressive'）
    :return: 最優資產權重
    """
    # 計算股票回報率
    returns = prices.pct_change().dropna()
    mean_returns = returns.mean()  # 平均回報率
    cov_matrix = returns.cov()  # 回報率的協方差矩陣

    # 定義投資組合的方差（風險）
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))

    # 定義投資組合的回報率
    def portfolio_return(weights):
        return np.dot(weights, mean_returns)

    num_assets = len(mean_returns)  # 資產數量
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})  # 權重和必須等於1
    bounds = tuple((0, 1) for _ in range(num_assets))  # 權重在0和1之間
    init_guess = num_assets * [1. / num_assets]  # 初始猜測的權重均等

    # 根據策略設置風險迴避參數
    if strategy == 'conservative':
        risk_aversion = 10
    elif strategy == 'balanced':
        risk_aversion = 1
    else:  # aggressive
        risk_aversion = 0.1

    # 定義目標函數，包含風險和回報的權衡
    def objective(weights):
        return risk_aversion * portfolio_variance(weights) - portfolio_return(weights)

    # 使用SLSQP方法進行優化
    result = sco.minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

def analyze_portfolio(investment_amount, tickers, strategy, period):
    """
    分析投資組合，計算最優資產配置、預期回報率、個別股票的預期回報率和預期獲利金額。
    
    :param investment_amount: 投資金額
    :param tickers: 股票代碼
    :param strategy: 投資策略
    :param period: 資料下載期間
    :return: 投資組合分析結果，包括投資計畫、預期回報率、個別股票的預期回報率和預期獲利金額
    """
    prices = get_stock_prices(tickers, period)  # 獲取股票價格
    optimal_weights = optimize_portfolio(prices, strategy)  # 獲取最優權重

    # 計算每檔股票的投資金額
    investment_plan = {ticker: weight * investment_amount for ticker, weight in zip(tickers, optimal_weights)}
    expected_return = np.sum(optimal_weights * prices.pct_change().mean()) * 252  # 年化收益率

    # 計算個別股票的預期回報率和預期獲利金額
    individual_returns = {ticker: prices.pct_change().mean()[ticker] * 252 for ticker in tickers}
    individual_profits = {ticker: investment_plan[ticker] * individual_returns[ticker] for ticker in tickers}

    result = {
        'investment_plan': investment_plan,
        'expected_return': expected_return,
        'individual_returns': individual_returns,
        'individual_profits': individual_profits
    }

    return result
