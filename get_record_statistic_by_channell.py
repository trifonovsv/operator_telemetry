## Скрипт построения диаграммы длительности ошибки записи записи каналов за сутки 
## Пример запуска "py <имя файла>.py <IP адрес> <дата>"
## <IP адрес> - имя папки в которой находится БД (По умолчанию ".\telemetry\192.168.11.109")
## <дата> - формат дд-мм-гггг, имя папки в которой находится БД за определенные сутки (По умолчанию .\telemetry\192.168.11.109\12-08-2022)

import os
import logging
import json
import shelve
import sys
from sys import argv
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date

from pprint import pprint
logging.basicConfig(level=logging.INFO, format='(%(asctime)s-%(levelname)s %(message)s')

_,ip,statistic_date=argv

file_path=os.path.join('telemetry',ip,statistic_date,'db_channel_record_statistic_v2')

with shelve.open(file_path) as shelve_file:
    dataFrame=shelve_file["channel_record_statistic_v2"]


y=dataFrame['channell_name']
y=np.array(y, dtype=float)
error_duration=dataFrame['error_duration']
error_duration=pd.to_timedelta(error_duration).dt.seconds



fig=plt.figure(figsize=(10,6) )
plt.barh(y,error_duration)
plt.gca().set(xlabel='Длительность (сек)',ylabel='Канал')

fig.suptitle(f'Длительность ошибки записи канала на сервере {ip}\n по состоянию на {statistic_date}')
plt.grid(True)
plt.tight_layout()
plt.show()
