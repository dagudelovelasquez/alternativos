# RPA
# David Agudelo
# ------------------------------------------------------------------------------
import pandas as pd
import os
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------
# Parámetros
# Directorio principal proyecto ('./General/data')
# path = os.path.join(os.getcwd(), '../..')

# data
path = os.path.join(os.getcwd(), './data')

# ------------------------------------------------------------------------------

# urls
url_root = 'http://www.cmfchile.cl/institucional/mercados/entidad.php?mercado=V&rut='
url_predicado = '&grupo=&tipoentidad=FINRE&row=AAAw%20cAAhAABP4OAAx&vig=VI&control=svs&pestania=7'

# selectores
path_input = '/html/body/div[2]/div[2]/div/div/div/div[3]/form/div[3]/input'
# '/html/body/div[1]/div[4]/div[3]/div[2]/form/div[3]/input'  # path anterior
path_tabla = '/html/body/div[2]/div[2]/div/div/div/div[3]/table'
7202-8

# '/html/body/div[1]/div[4]/div[3]/div[2]/table'  # path anterior
selector_rs = "./dt[.='Razón Social: ']/following-sibling::dd"  # razón social
selector_rut = "./dt[.='RUT:']/following-sibling::dd"
# //*[@id="contenido"]/div[2]
# /html/body/div[2]/div[2]/div/div/div/div[3]/table
# /html/body/div[2]/div[2]/div/div/div/div[3]/div[2]/table
# //*[@id="contenido"]/div[2]/table
# //*[@id="contenido"]/table
# //*[@id="contenido"]/div[2]
# fechas
d_ini = "31"
m_ini = "12"
y_ini = '2014'

d_fin = '31'
m_fin = '12'
y_fin = '2022'

# ------------------------------------------------------------------------------
# FONDOS
file_name = 'T_ALTERNATIVOS'
data = pd.read_csv(
                    path + '/catalogos/' + file_name + '.csv',
                    header=0, sep=',',
                    index_col='RUN',
                    encoding='iso-8859-1'
                    )
data.columns = data.columns.str.upper()
T_ALTERNATIVOS = data.sort_index()  # del antiguo al mas reciente

FONDOS = T_ALTERNATIVOS[T_ALTERNATIVOS['SOURCE'] == 'SVS'].index.values

# ------------------------------------------------------------------------------
# importar datos
for i in FONDOS:
    driver = webdriver.Chrome('./chromedriver.exe')
    driver.maximize_window()
    url = url_root + str(i) + url_predicado
    driver.get(url)

    # --------------------------------------------------------------------------
    # dia inicial
    try:
        seleccionar_dia = driver.find_element_by_name("dia1")
        Select(seleccionar_dia).select_by_visible_text(d_ini)
        sleep(random.uniform(1.0, 2.0))
    except:
        break
    # mes inicial
    try:
        seleccionar_mes = driver.find_element_by_name("mes1")
        Select(seleccionar_mes).select_by_visible_text(m_ini)
        sleep(random.uniform(1.0, 2.0))
    except:
        break
    # año inicial
    try:
        seleccionar_ano = driver.find_element_by_name("anio1")
        Select(seleccionar_ano).select_by_visible_text(y_ini)
        sleep(random.uniform(1.0, 2.0))
    except:
        break

    # --------------------------------------------------------------------------
    # dia final
    try:
        seleccionar_dia = driver.find_element_by_name("dia2")
        Select(seleccionar_dia).select_by_visible_text(d_fin)
        sleep(random.uniform(1.0, 2.0))
    except:
        break
    # mes final
    try:
        seleccionar_mes = driver.find_element_by_name("mes2")
        Select(seleccionar_mes).select_by_visible_text(m_fin)
        sleep(random.uniform(1.0, 2.0))
    except:
        break
    # año final
    try:
        seleccionar_ano = driver.find_element_by_name("anio2")
        Select(seleccionar_ano).select_by_visible_text(y_fin)
        sleep(random.uniform(1.0, 2.0))
    except:
        break

    # --------------------------------------------------------------------------
    # search_button = driver.find_element_by_xpath(path_input)
    search_button = driver.find_element_by_name('sub_consulta_fi')  # path_input
    search_button.click()
    sleep(random.uniform(1.0, 3.0))

    # --------------------------------------------------------------------------
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, path_tabla)))
    except:
        sleep(random.uniform(2.0, 4.0))
    tabla = driver.find_element_by_xpath(path_tabla)

    soup = BeautifulSoup(driver.page_source, 'lxml')  # Parse the HTML as a str
    table = soup.find_all('table')[0]

    # encabezados
    if len(table.find_all('th')) == 10:
        i = 0
        columnas = []
        for c in table.find_all('th'):
            c_name = str(c.get_text()).strip()
            i += 1
            columnas.append(c_name)
        # I know the size
        new_table = pd.DataFrame(columns=range(0, 10), index=[0])
        df = pd.DataFrame()
        i = 0
        for row in table.find_all('tr'):
            j = 0
            columns = row.find_all('td')
            for column in columns:
                new_table.iat[i, j] = column.get_text()
                j += 1
            df = pd.concat([df, new_table])
        df = df.dropna(axis=0, how='all')
        df.columns = columnas
        df = df.set_index('Fecha')
    else:
        df = pd.DataFrame()

    # --------------------------------------------------------------------------
    # Descripción
    descripcion = driver.find_element_by_id('datos_ent')
    razon_social = descripcion.find_element_by_xpath(selector_rs).text
    rut = descripcion.find_element_by_xpath(selector_rut).text

# ------------------------------------------------------------------------------
    file_name = rut + '_' + razon_social
    df.to_csv(
            path + '/vc_chile/raw/' + file_name + '.csv',
            encoding='iso-8859-1'
            )
    driver.quit()

# ------------------------------------------------------------------------------
