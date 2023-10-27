import requests
from bs4 import BeautifulSoup
import numpy as np
from scipy.interpolate import UnivariateSpline
import pandas as pd

def yieldsbr(Initial_Date, Final_Date, Maturities, output_file):
    dates = pd.date_range(start=Initial_Date, end=Final_Date, freq='D', tz='UTC').strftime('%d-%m-%Y').tolist()
    mat = np.empty((len(dates), len(Maturities)))

    # Contador para preencher a matriz mat
    i = 0
    # Scrape the data from the BM&F website
    for date in (dates):
        url = f'https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data={date}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table is not None:
                rows = table.find_all('td')
                td_text = [td.get_text() for td in rows]

                # Cria a matriz data que será usada para criar a spline
                data = pd.DataFrame({'Dias Corridos': [int(td_text[i]) for i in range(0, len(td_text), 3)],
                    'V2': [float(td_text[i].replace(',', '.')) for i in range(1, len(td_text), 3)],
                    'V3': [float(td_text[i].replace(',', '.')) for i in range(2, len(td_text), 3)]})
                
                # Realiza a interpolação dos dados e cria a matriz de retorno
                data_to_array = data.to_numpy()
                t = np.array(data_to_array[:, 0], dtype=int) / 21
                y = np.array(data_to_array[:, 1], dtype=float)
                spl = UnivariateSpline(t, y, s=0)
                t_new = np.array(Maturities)
                new = spl(t_new)
                
                if i < len(dates):
                    mat[i, :] = new
                    i += 1
            
            else:
                print(f"No tables found for {date}")
        else:
            print(f"Failed to retrieve data for {date}")

    # Create a DataFrame with the results
    colnames = [f"M{m}" for m in Maturities]
    mat = mat[np.apply_along_axis(np.isfinite, 1, mat).all(axis=1)]

    # Constrói DataFrame final e salva em CSV
    df = pd.DataFrame(mat, index=dates, columns=colnames)
    print(df)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file)

# Example
Initial_Date = '2023/08/25'  # Available from 2003-08-08. YYYY-MM-DD
Final_Date = '2023/10/25'
Maturities = [1, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 48, 60, 72]
output_file = 'output.csv'

yieldsbr(Initial_Date=Initial_Date, Final_Date=Final_Date, Maturities=Maturities, output_file=output_file)
