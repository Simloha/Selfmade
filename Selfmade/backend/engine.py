# /backend/engine.py
import numpy as np
import scipy.stats as si

def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """Calculates theoretical Black-Scholes asset value."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0) if option_type == 'call' else max(K - S, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type.lower() == 'call':
        return S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)

def calculate_black_scholes_greeks(S, K, DTE, r, IV, option_type='call'):
    """Calculates local option risk parameters."""
    T = max(DTE, 1e-5) / 365.0
    sigma = max(IV, 1e-4) / 100.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    pdf_d1 = si.norm.pdf(d1)
    if option_type.lower() == 'call':
        delta = si.norm.cdf(d1)
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2)) / 365.0
    else:
        delta = si.norm.cdf(d1) - 1.0
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2)) / 365.0
    
    vega = (S * pdf_d1 * np.sqrt(T)) / 100.0
    return round(delta, 4), round(theta, 2), round(vega, 2)

def solve_implied_volatility(market_price, S, K, DTE, r, option_type='call'):
    """Newton-Raphson optimization matrix reversing market prices into IV values."""
    T = max(DTE, 1e-5) / 365.0
    intrinsic = max(S - K, 0.0) if option_type == 'call' else max(K - S, 0.0)
    if market_price <= intrinsic:
        return 0.0
        
    sigma_guess = 0.25
    for _ in range(50):
        current_price = black_scholes_price(S, K, T, r, sigma_guess, option_type)
        error = current_price - market_price
        if abs(error) < 1e-4:
            return round(sigma_guess * 100.0, 2)
        d1 = (np.log(S / K) + (r + 0.5 * sigma_guess ** 2) * T) / (sigma_guess * np.sqrt(T))
        vega = S * si.norm.pdf(d1) * np.sqrt(T)
        if vega < 1e-5:
            break
        sigma_guess -= error / vega
        if sigma_guess <= 0 or sigma_guess > 4.0:
            break
    return 15.0 # Stable baseline fallback threshold
