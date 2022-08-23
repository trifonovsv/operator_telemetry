## Скрипт для построения графиков статистики потребления ресурсов 
## Пример запуска на Linux: "python3 <имя файла>.py localhost 22-08-2022"
## Пример запуска на Windows: "py <имя файла>.py localhost 22-08-2022"
## Где localhost - имя папки где хранится БД с данными
## Где 22-08-2022 - дата (она же имя вложенной папки) за которую необходимо построить статистику
## Доработано с учетом особенностей Linux
import os
import logging
import json
import shelve
import sys
from sys import argv
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pprint import pprint
logging.basicConfig(level=logging.INFO, format='(%(asctime)s-%(levelname)s-%(message)s')

_,ip,date=argv

file_path=os.path.join('telemetry',ip,date,'db')

with shelve.open(file_path) as shelve_file:
    dataFrame=shelve_file["harware_state_history"]


x=dataFrame['time']

y=dataFrame['cpu_usage']
yy=dataFrame['ram_free']
yy=np.array(yy, dtype=float)
yyy=dataFrame['network_usage_down']
yyy=np.array(yyy, dtype=float)
yyyy=dataFrame['network_usage_up']
yyyy=np.array(yyyy, dtype=float)
print("Построение графиков cpu_usage, ram_free и network_usage")




fig=plt.figure(figsize=(10,6) )
fig.suptitle(f'Ресурсы сервера {ip}\n за {date}')
plt.subplot(311)

plt.fill_between(x,yyy,0, label='download',alpha = 0.5)
plt.fill_between(x,yyyy,0, label='upload',alpha = 0.5)
plt.legend(loc='upper left')
plt.grid(True)

plt.ylabel('network_usage, \nbytes per sec')
plt.ylim(0)

plt.subplot(312)
plt.fill_between(x,y,alpha = 0.5)
plt.grid(True)
plt.ylim(0,100)
plt.ylabel('cpu, %')

plt.subplot(313)
plt.fill_between(x,yy,alpha = 0.5)
plt.grid(True)
plt.ylim(0,100)
plt.ylabel('ram_free, %')
plt.xlabel('Время')

plt.show()
