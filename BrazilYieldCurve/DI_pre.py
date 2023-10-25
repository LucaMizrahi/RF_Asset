import requests
from bs4 import BeautifulSoup
import numpy as np
from scipy.interpolate import UnivariateSpline
import pandas as pd

def yieldsbr(Initial_Date, Final_Date, Maturities, output_file):
    dates = pd.date_range(Initial_Date, Final_Date)
    mat = np.empty((len(dates), len(Maturities)))

    for i, date in enumerate(dates):
        date_str = date.strftime('%d/%m/%Y')
        url = f'https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data={date_str}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table is not None:
                rows = table.find_all('td')
                if len(rows) > 1:
                    data = []
                    for row in rows[:]:
                        print('\n==================',row,'==================\n')

                        cols = row.find_all('tr')
                        data.append([col.text.strip().replace(".", "").replace(",", ".") for col in cols])
                    data = np.array(data, dtype=float)
                    # t = data[:, 0] / 21
                    # y = data[:, 1]
                    # spl = UnivariateSpline(t, y)
                    # t_new = np.array(Maturities)
                    # new = spl(t_new)
                    # mat[i, :] = new
                    print(f"Processed {date_str}")
                else:
                    print(f"No data for {date_str}")
            else:
                print(f"No tables found for {date_str}")
        else:
            print(f"Failed to retrieve data for {date_str}")

    # Create a DataFrame with the results
    df = pd.DataFrame(mat, columns=[f'M{m}' for m in Maturities], index=dates)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file)

# Example
Initial_Date = '2023-10-25'  # Available from 2003-08-08. YYYY-MM-DD
Final_Date = '2023-10-25'
Maturities = [1, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 48, 60, 72]
output_file = 'output.csv'

yieldsbr(Initial_Date=Initial_Date, Final_Date=Final_Date, Maturities=Maturities, output_file=output_file)
