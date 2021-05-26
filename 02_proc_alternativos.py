# Autor: David Agudelo Velásquez
# Consolidador de inputs
# Descripión: Este procedimiento agregar los archivos de la cartera
import pandas as pd
import os
from funciones import *
import datetime as dt
import matplotlib.pyplot as plt

# Directorio principal proyecto
dir = 'C:/Users/dagudelo/SURA Chile S.A/TAA - Documentos/General'
os.chdir(dir + '/data/Alternativos/raw')
cwd = os.getcwd()

# Data
files = os.listdir()

valores_cuota = pd.DataFrame()
for x in files:
    data = pd.read_csv(
                        x,
                        # index_col='Fecha',
                        encoding='iso-8859-1',
                        decimal=','
                        )
    data['SOURCE'] = x
    valores_cuota = pd.concat([valores_cuota, data])
    print(x)

# eliminar las lineas con encabezados que hayan quedado dentro del append
valores_cuota['RUN'] = valores_cuota['SOURCE'].str[:4]
valores_cuota.Fecha = pd.to_datetime(valores_cuota.Fecha, format="%d/%m/%Y")
valores_cuota = valores_cuota.set_index('Fecha')
df = pd.DataFrame(valores_cuota[['RUN', 'Valor Económico']], valores_cuota.index)
df = df.reset_index().drop_duplicates(['Fecha', 'RUN'])
df = df.pivot(index='Fecha', columns='RUN', values='Valor Económico')
df.index = pd.DatetimeIndex(df.index)
# df = df.apply(lambda x: x.str.replace(',','.'))
df_p = df.sort_index(ascending=True)
df_p = df_p.asfreq(freq='D', method='ffill')
df_p = df_p.fillna(method='ffill')

# ------------------------------------------------------------------------------
# TABLA Alternativos
dir = 'C:/Users/dagudelo/SURA Chile S.A/TAA - Documentos/General/data/catalogos'
T_ALTERNATIVOS = pd.read_csv(
                            dir + '/T_ALTERNATIVOS.csv',
                            header=[0],
                            encoding='iso-8859-1'
                        )
T_ALTERNATIVOS = T_ALTERNATIVOS.set_index('RUN')

# ------------------------------------------------------------------------------
# precios en USD
#   MONEDAS
dir = 'C:/Users/dagudelo/SURA Chile S.A/TAA - Documentos/General/data/series'
price_CURRENCY = pd.read_csv(
                            dir + '/clean/CURRENCY.csv',
                            index_col='FECHA',
                            parse_dates=True
                        )
price_CURRENCY.columns = price_CURRENCY.columns.str.upper()

fondos = df_p.columns
df_p_USD = pd.DataFrame()
n = 0
error = ()
for i in fondos:
    n += 1
    m = T_ALTERNATIVOS.loc[i]['MONEDA_ESTANDAR']  # selecciona la moneda
    if m is np.nan:
        e = 'ERROR, no se encuentra moneda NaN para %s' % i
        error = np.append(error, e)
    elif (m == 'USD'):
        df_p_USD[i] = df_p[i]
        print('OK en USD')
    elif (m == 'EUR') or (m == 'GBP') or (m == 'AUD'):
        df_p_USD[i] = df_p[i] * price_CURRENCY[m + ' CURNCY']
        print('OK en USD')
    elif (m == 'CAD') or (m == 'BRL') or \
            (m == 'CLP') or (m == 'JPY') or \
            (m == 'MXN') or (m == 'HKD') or \
            (m == 'SEK') or (m == 'CHF') or (m == 'CNH'):
        df_p_USD[i] = df_p[i] / price_CURRENCY[m + ' CURNCY']
        print('OK en USD')
    else:
        e = 'No se tienen los precios para %s' % m
        error = np.append(error, e)
print(error)

# ------------------------------------------------------------------------------
fecha_ini = valores_cuota.sort_index().index[0]
# Guaranteed to get the next month. Force any_date to 28th and then add 4 days.
next_month = fecha_ini.replace(day=28) + dt.timedelta(days=4)
# Subtract all days that are over since the start of the month.
fecha_ini = next_month - dt.timedelta(days=next_month.day)
fecha_inicial = str((fecha_ini).date())
fecha_fin = valores_cuota.sort_index(ascending=False).index[0]
fecha_final = str((fecha_fin + dt.timedelta(days=(0))).date())

# ------------------------------------------------------------------------------
df_p_USD = df_p_USD.asfreq('D').ffill().replace(0, np.nan)
df_r_peers = retorno(series=df_p_USD, frecuencia='M')
df_r_PG = pd.DataFrame(df_r_peers.mean(axis=1))
df_r_PG.columns = ['PG']

df_p_USD.loc[fecha_inicial]
I_peers = I_return_acum(
                        retornos=df_r_peers, frecuencia='B',
                        base=100, fecha_ini=fecha_inicial)
I_PG = I_return_acum(
                    retornos=df_r_PG, frecuencia='M',
                    base=100, fecha_ini=fecha_inicial)

df_r_PG.std()*(12**(1/2))
df_r_PG.max()
df_r_PG.min()
I_peers.plot()
I_PG.plot()

# df_r_top_3 =
df_p_USD.columns

r = df_r_peers[['9165', '9314', '9337']]
I_peers = I_return_acum(retornos=pd.DataFrame(r.mean(axis=1)), frecuencia='M', base=100, fecha_ini=fecha_inicial)

I_peers.columns = ['PG']
I_peers.plot()
# FONDO_INVERTIDO = LU1542613549 --- HGEMIUA LX Equity

# ------------------------------------------------------------------------------
df_p_USD
df_r_peers_daily = retorno(series=df_p_USD, frecuencia='D')
df_r_PG_daily = pd.DataFrame(df_r_peers_daily.mean(axis=1))
df_r_PG_daily.columns = ['PG']
df_r_PG_daily.plot()

# problema están saliendo un infinito
I_PG_INVER = I_return_acum(
                            retornos=df_r_PG_daily,
                            frecuencia='B',
                            base=100,
                            fecha_ini='2020-03-31'
                            )
I_PG_INVER[fecha_inicial:'2020-12-31'].plot()

plt.figure(1, figsize=(18, 4))
plt.plot((I_PG_INVER-100)[fecha_inicial:'2020-12-31'])
plt.show()

# # Eliminar espacios de run
# cartera[3].astype(str).str.strip().unique()
# cartera.to_csv('../cartera.txt')
# dir = 'C:/Users/dagudelo/SURA Chile S.A/Fund Selection - General/Iniciativas/Alternativos/Alternativos - AFPs/'
# p_fondo = pd.read_csv(
#                     dir + 'p_fondos.csv',
#                     index_col=0, parse_dates=True,
#                     encoding='iso-8859-1')
dir = 'C:/Users/dagudelo/SURA Chile S.A/TAA - Documentos/General/data/series'
p_fondo = pd.read_csv(
                    dir + '/clean/FUNDS_TR_INDEX.csv',
                    index_col=0, parse_dates=True,
                    encoding='iso-8859-1')['HGEMIUA LX EQUITY']
p_fondo = pd.DataFrame(p_fondo)
p_fondo.index.name = 'FECHA'
p_fondo = p_fondo.sort_index(ascending=True)
p_fondo = p_fondo.asfreq(freq='D', method='ffill')
p_fondo = p_fondo.fillna(method='ffill')
r_fondo_alternativo = retorno(series=p_fondo, frecuencia='D')

I_fondo_invertido = I_return_acum(
                            retornos=r_fondo_alternativo,
                            frecuencia='D',
                            base=100,
                            fecha_ini='2020-03-31'
                            )

plt.plot((I_PG_INVER-100)[fecha_inicial:'2020-12-31'])
plt.plot((I_fondo_invertido-100)[fecha_inicial:'2020-12-31'])
plt.show()
dir = 'C:/Users/dagudelo/SURA Chile S.A/Fund Selection - General/Iniciativas/Alternativos/Alternativos - AFPs/'
I_PG_INVER.to_csv(dir + 'pg.csv')
p_fondo.to_csv(dir + 'p_fondo.csv')
