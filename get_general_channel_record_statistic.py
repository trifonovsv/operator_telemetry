## Скрипт построения графика статиcтики записи каналов за сутки 
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

file_path=os.path.join('telemetry',ip,statistic_date,'db_channel_recordings')

with shelve.open(file_path) as shelve_file:
    dataFrame=shelve_file["channel_recordings"]
    logging.debug(f'\n{dataFrame.head(5)}')

x=dataFrame['time']
y=dataFrame['total_recording_channels']
y=np.array(y, dtype=float)
# Для построения оси y cформируем ряд целых значений
yint=[]
for i in range(int(y.max())):
    yint.append(i+1)
yy=dataFrame['fail_channel_recordings']
yy=np.array(yy, dtype=float)
fig=plt.figure(figsize=(10,6) )

plt.fill_between(x,y,0, color='g', label='Общее количество\nзаписываемых каналов',alpha = 0.5)
plt.fill_between(x,yy,0, color='r', label='Каналы со сбоями записи',alpha = 0.5)
plt.legend(loc='upper right')
plt.grid(True)

if len(yint)<10:
    plt.yticks(yint)

#Описание подписей на графике и осях
#Нарисуем проекцию на ось максимального значения 
s=np.where(dataFrame['fail_channel_recordings'] == yy.max())
select_indices = list(s)[0]
xmax_index=select_indices[-1]    #линия начинается у последнего индекса когда был зафиксирован максимум
arrowprops={'arrowstyle': '-', 'ls':'--', 'color':'r','alpha': 0.5}
x,y=x[xmax_index],yy.max()
plt.annotate(str(int(yy.max())), xy=(x,y), xytext=(-0.01, y), 
             textcoords=plt.gca().get_yaxis_transform(), arrowprops=arrowprops, 
             va='center', ha='right',color='r')

#Добавляем заголовок
timestamp=dataFrame["time"][0]
timestamp_date=timestamp.date()
fig.suptitle(f'Статистика записи каналов на сервере {ip}\n по состоянию на {timestamp_date.day}.{timestamp_date.month}.{timestamp_date.year}')
#Добавляем подписи осей
plt.ylabel('Количество каналов')
plt.xlabel('Время')
plt.ylim(0)
# оптимизируем поля и расположение объектов
plt.tight_layout()
plt.show()