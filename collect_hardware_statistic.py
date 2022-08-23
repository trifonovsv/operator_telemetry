## Скрипт для построения графиков статистики потребления ресурсов
## Пример запуска на Windows: "py collect_hardware_statistic.py localhost 'enp2s0'" 
## Пример запуска на Linux: "python3 collect_hardware_statistic.py localhost 'enp2s0'"
## Где 'enp2s0' - имя сетевого интерфейса
## Где localhost - имя папки для хранения БД
## Доработано с учетом особенностей Linux
import psutil
import time
import sys
import logging
import json
import shelve
import sys
from sys import argv
import time
import datetime
import os
import pandas as pd
from datetime import datetime

if sys.platform=='linux':
    pass #import getch
else:
    import msvcrt

import logging
logging.basicConfig(level=logging.INFO, format = '%(asctime)s - %(levelname)s %(message)s')

def get_hardware_stat(net_name):
    inteval=5                                                #Интервал проверки
    previous_state=psutil.net_io_counters(pernic=True)       #Статистика сети
    previous_state["timestamp"] = datetime.now()             #Добавляем метку времени в объект статуса сети

    cpu_usage=psutil.cpu_percent(interval=inteval)           #Получаем нагрузку ЦП за указанный промежуток времени

    current_state=psutil.net_io_counters(pernic=True)        #Обновим статистику сети
    current_state["timestamp"] = datetime.now()              #И добавим новую метку 
    time_diff = current_state["timestamp"] - previous_state["timestamp"]
    time_diff_in_seconds = time_diff.total_seconds()
    down_diff=getattr(current_state[net_name], 'bytes_recv')-getattr(previous_state[net_name], 'bytes_recv')
    up_diff=getattr(current_state[net_name], 'bytes_sent')-getattr(previous_state[net_name], 'bytes_sent')
    network_usage_down = down_diff / time_diff_in_seconds             #Подсчитали колличество байт за указанный промежуток
    network_usage_up = up_diff / time_diff_in_seconds
    ram_free=psutil.virtual_memory().available * 100 / psutil.virtual_memory().total    #Получили процент свободной памяти

    return cpu_usage, ram_free, network_usage_down, network_usage_up


def get_current_time():
    currentTime=datetime.now()
    return currentTime

def create_data_frame(file_path):
    columns=['time', 'cpu_usage', 'ram_free','network_usage_down', 'network_usage_up']
    newDataFrame=pd.DataFrame(columns=columns)

    with shelve.open(file_path) as shelve_file:
        shelve_file["harware_state_history"]=newDataFrame


def is_db_file_exist(host):
    folder_name=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y')))
    file_path=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db'))
    file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db'))}.dat"
    
    if sys.platform=='linux':
        file_path_linux=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db'))}.db"
    else:
        file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db'))}.dat"
    
    logging.debug(f'is exist db folder: {os.path.exists(folder_name)}')
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    time.sleep(0.1)  #таймер для того что бы создалась директория

    if sys.platform=='linux':
        logging.debug(f'OS Linux: is exist db file: {os.path.exists(file_path_linux)}')
    else:
        logging.debug(f'is exist db file: {os.path.exists(file_path_windows)}')

    if sys.platform=='linux':
        if not os.path.exists(file_path_linux):   # Проверка на существование файла с заданным именем
            logging.debug(f'OS Linux: creating data_frame file')
            create_data_frame(file_path)
    else:
        if not os.path.exists(file_path_windows):   # Проверка на существование файла с заданным именем
            logging.debug('creating data_frame file')
            create_data_frame(file_path)
    return folder_name, file_path, file_path_windows 
    
def update_data_frame(time, cpu_usage, ram_free,network_usage_down, network_usage_up,file_path):

    with shelve.open(file_path) as shelve_file:
        dataFrame=shelve_file["harware_state_history"]
    new_data=pd.DataFrame({"time":time,
    "cpu_usage":cpu_usage,
    "ram_free":ram_free,
    "network_usage_down":network_usage_down,
    "network_usage_up":network_usage_up},
    index=[0])
    frames=[dataFrame,new_data]
    updatedDataFrame=pd.concat(frames,ignore_index=True)
    with shelve.open(file_path) as shelve_file:
        shelve_file["harware_state_history"]=updatedDataFrame

def check_exit_button(): # функция завершения работы по нажатию клавиши ESC
    if sys.platform=='linux':
        pass
    else:
        if msvcrt.kbhit(): #если нажата клавиша
            if ord(msvcrt.getch()) == 27: #считываем код клавиши, если клавиша ESC
                logging.info(f' Завершение работы: ESC')
                sys.exit() # завершаем программу
        else:
            pass

def check_harware_info(host,net_name):
    while True:
        _,db_file_path,_=is_db_file_exist(host)
        current_cpu_usage, current_ram_free, network_usage_down,network_usage_up=get_hardware_stat(net_name)
        current_time=get_current_time()
        logging.info(f'localhost: cpu(%) -> {round(current_cpu_usage,2)}, ram_free(%) -> {round(current_ram_free,2)}, network_usage(Kbyte/sec) UP/DOWN -> {round(network_usage_up/1000)} / {round(network_usage_down/1000)}')
        update_data_frame(current_time, current_cpu_usage, current_ram_free,network_usage_down,network_usage_up,db_file_path)
        if sys.platform!='linux':
            check_exit_button()
        else:
            pass
        time.sleep(5)


# ------исполняемый код скрипта-------

if __name__ == '__main__':
    _,host,net_name=argv
    while True:
        try:
            check_harware_info(host,net_name)
        except KeyboardInterrupt:    #Без этой строчки код будет выполняться бесконечно при любом количестве ошибок
            logging.info(f' Завершение работы: KeyboardInterrupt')
            is_running=False
            sys.exit(0)
        except Exception as e:
            logging.info(f'ERROR: {e}')
            time.sleep(1)    #Перезапуск процесса скрипта спустя n сек
