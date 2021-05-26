# ------------------------------------------------------------------------------
# Autor: David Agudelo Velásquez
# funciones del proceso de seleccion de fondos
# ------------------------------------------------------------------------------
# Paquetes
import numpy as np
import pandas as pd
import math

print(__name__)


# Retornos
def retorno(series, frecuencia='parametroFrecuecia'):
    series = series.sort_index()
    ret = series.asfreq(freq=frecuencia, method='ffill').pct_change()
    return(ret)


# Indice de retorno Acumulado
def I_return_acum(retornos, frecuencia='parametroFrecuecia',
                base=100, fecha_ini=''):
    retornos = retornos.sort_index()
    if fecha_ini == '':
        fecha_ini = retornos.iloc[0].name
    retornos = retornos.loc[fecha_ini:].replace(np.nan, 0)
    retornos.loc[fecha_ini][-np.isnan(retornos.loc[fecha_ini])] = 0
    if frecuencia == 'D':
        R_acum = retornos.asfreq(freq='D', fill_value=0)
        index_Acum = (1+R_acum).cumprod()*base
    elif frecuencia == 'B':
        R_acum = retornos.asfreq(freq='B', fill_value=0)
        index_Acum = (1+R_acum).cumprod()*base
    elif frecuencia == 'W':
        R_acum = retornos.asfreq(freq='W', fill_value=0)
        index_Acum = (1+R_acum).cumprod()*base
    elif frecuencia == 'M':
        R_acum = retornos.asfreq(freq='M', fill_value=0)
        index_Acum = (1+R_acum).cumprod()*base
    elif frecuencia == 'Y':
        R_acum = retornos.asfreq(freq='Y', fill_value=0)
        index_Acum = (1+R_acum).cumprod()*base
    return(index_Acum)


# Rolling return a partir de retornos retornos_mensuales
def rolling_return(series, window):
    series = series.sort_index(ascending=False)
    r = (1+series).rolling(window)
    prod = (r.agg(lambda x: x.prod())-1).shift(-window+1)
    return prod


# Media movil
def moving_average(series, window):
    series = series.sort_index(ascending=False)
    x = series.rolling(window)
    m = x.mean().shift(-window+1)
    return(m)


# z-score
def zscore(x, window, ddof=1):
    x = x.sort_index(ascending=False)
    r = x.rolling(window)
    m = r.mean().shift(-window+1)
    s = r.std(ddof=ddof).shift(-window+1)
    z = (x-m)/s
    z = z.replace(
                    [-np.inf, np.inf, np.nan],
                    np.nan
                )
    return z


# 1er Quintil
def primer_quintil(var):
    Q1 = np.ceil(var.rank(axis=1, ascending=False, pct=True).mul(5))
    Q1 = Q1.sort_index(ascending=False)
    Q1[Q1 > 1] = np.nan   # Deja solo el primer quintil
    return(Q1)


# Top
def top(var, n):
    r = var.rank(axis=1, ascending=False, pct=False)
    t = r.sort_index(ascending=False)
    t[t > n] = np.nan   # Deja solo el primer quintil
    return(t)


# Bottom
def bottom(var, n):
    r = var.rank(axis=1, ascending=True, pct=False)
    b = r.sort_index(ascending=False)
    b[b > n] = np.nan   # Deja solo el primer quintil
    return(b)


# 1er Quintil por z-score
def q1_zscore(var, window):
    z = zscore(x=var, window=window, ddof=1)
    Q1 = np.ceil(z.rank(axis=1, ascending=False, pct=True).mul(5))
    Q1[Q1 > 1] = np.nan   # Deja solo el primer quintil
    return(Q1)


# Volatilidad
def volatilidad(x, window, ddof=1):
    x = x.sort_index(ascending=False)
    r = x.rolling(window)
    s = r.std(ddof=ddof).shift(-window+1)
    return(s)


# Information Ratio rolling
# r_mensual debe ser un DataFrame
# def ir_rolling(r_mensual, r_mensual_bench, window, ddof=1):
#     a_mensual = pd.DataFrame()
#     for x in r_mensual:
#         a = r_mensual[x] - r_mensual_bench
#         a_mensual[x] = a
#     x = a_mensual.sort_index(ascending=False)
#     a = x.rolling(window)
#     a_mean = a.mean().shift(-window+1)
#     TE = a.std(ddof=ddof).shift(-window+1)
#     IR = (a_mean/TE) * math.sqrt(12)  # annualized
#     return(IR)

# para un vector contra vector(pd.Series), el anterior es con df
def ir_rolling(df_r_port, df_r_bench, window, ddof=1):
    a = df_r_port - df_r_bench
    x = a.sort_index(ascending=False)
    a = x.rolling(window)
    a_mean = a.mean().shift(-window+1)
    TE = a.std(ddof=ddof).shift(-window+1)
    IR = (a_mean/TE) * math.sqrt(12)  # annualized
    return(IR)


# Retorno de un Portafolio
def portfolio_return(w, r):
    Ri = w * r
    Rp = pd.DataFrame(Ri.sum(axis=1))
    return(Rp)


# Probabilidad de exito
def prob_exito(var):
    n_pos = (var[var > 0]).count()
    p = n_pos / var.count()
    return(p)


# Arreglo rolling para formulas
def rolling_apply(df, n_periods, func, min_periods):
    df = df.sort_index()
    if min_periods is None:
        min_periods = n_periods
    result = pd.Series(np.nan, index=df.index)

    for i in range(1, len(df)+1):
        sub_df = df.iloc[max(i-n_periods, 0):i, :].dropna()  # I edited here
        if len(sub_df) >= min_periods:
            idx = sub_df.index[-1]
            result[idx] = func(sub_df)
    return(result)


# Beta rolling
def beta_rolling(x, y, window):
    x = x.sort_index().rolling(window)
    y = y.sort_index().rolling(window)

    cov_xy = x.cov(y)
    var_x = x.var()
    b = cov_xy/var_x
    beta = b.sort_index(ascending=False)
    return(beta)
