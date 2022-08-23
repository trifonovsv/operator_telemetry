## Скрипт сбора информации о длительности ошибки записи по каждому каналу и количестве каналов со сбоями
## Пример запуска "py <имя файла>.py <IP адрес>
## <IP адрес> - адрес наблюдаемого сервера, он же имя папки в которой сохраняется БД (По умолчанию ".\telemetry\192.168.11.109")

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
import requests
import pandas as pd
from datetime import datetime

if sys.platform=='linux':
    pass #import getch
else:
    import msvcrt

import logging
logging.basicConfig(level=logging.INFO, format = '%(asctime)s - %(levelname)s %(message)s')

def authorization(host):
    ## Метод интеграции на сервере

    method='/v1/authorization/login'
    url = f'http://{host}:8090{method}'
    ## Заголовок для отправки в формате json
    headers = {'Content-type': 'application/json',  
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8'
               }
    ## Данные тела запроса
    data ={"login": 'admin',
           "password": 'admin',
           "encryptionType": "None"
          }
    ## Формирование запроса
    response=requests.post(url, headers=headers, data = json.dumps(data))    ## Присвоил переменной данные ответа сервера объект JSON
    try:    ## Пытаемся перехватить ошибку если вместо json объектра сервер ответил кодом 200, но не вернул json объект 
        responseData = response.json()    ## Присвоил переменной данные ответа сервера объект JSON
    except:    ## Если возникает какая либо ошибка переменная принимает значение заглушки в JSON
        responseData={"accessToken": "None",
                      "currentServer": "Some Error with JSON object"}
    server_guid = responseData['currentServer'] ## Получаем GUID сервера
    token = responseData['accessToken']    ## Готовая конструкция для дальнейшего использования токена
    return token

def get_channel_recordings(host, token):
    #/v1/channel/recordings
    method='/v1/channel/recordings'
    url=f'http://{host}:8090{method}'
    headers = {'Content-type': 'application/json',  
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8',
               'Authorization': f'bearer {token}'
               }
    response=requests.get(url, headers=headers)
    return response.text

def get_current_time():
    currentTime=datetime.now()
    return currentTime

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

def get_device_name(host,token,channel_guid):
    ## Метод интеграции на сервере
    method='/v1/channel/guid'
    url = f'http://{host}:8090{method}'
    ## Заголовок для отправки в формате json
    headers = {'Content-type': 'application/json',  
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8',
               'Authorization': f'bearer {token}'
               }
    ## Данные тела запроса
    payload =json.dumps(channel_guid)
    ## Формирование запроса
    response=requests.post(url, headers=headers, data = payload)
    try:    ## Пытаемся перехватить ошибку если вместо json объектра сервер ответил кодом 200, но не вернул json объект 
        responseData = response.json()    ## Присвоил переменной данные ответа сервера объект JSON
        logging.info(f'channel {responseData["coupledDevice"]["ip"]}. responseData["coupledDevice"]["ip"]=="0.0.0.0": {responseData["coupledDevice"]["ip"]=="0.0.0.0"}')
        if responseData["coupledDevice"]["ip"]=="0.0.0.0":
            channell_name=f'{responseData["coupledDevice"]["name"]} {responseData["name"]}'
        else:
            channell_name=f'{responseData["coupledDevice"]["ip"]} {responseData["name"]}'
    except:    ## Если возникает какая либо ошибка переменная принимает значение заглушки в JSON
        channell_name=None
    return channell_name

def create_data_frame_v1(file_path):
    columns=['time', 'total_recording_channels', 'fail_channel_recordings']
    newDataFrame=pd.DataFrame(columns=columns)

    with shelve.open(file_path, flag='n') as shelve_file:
        shelve_file["channel_recordings"]=newDataFrame

def is_db_file_exist_v1(host):
    folder_name=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y')))
    file_path=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_recordings'))
    file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_recordings'))}.dat"
    
    if sys.platform=='linux':
        file_path_linux=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_recordings'))}.db"
    else:
        file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_recordings'))}.dat"
    
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
            create_data_frame_v1(file_path)
    else:
        if not os.path.exists(file_path_windows):   # Проверка на существование файла с заданным именем
            logging.debug('creating data_frame file')
            create_data_frame_v1(file_path)
    
    return folder_name, file_path, file_path_windows

def update_data_frame_v1(fail_channel_recordings,total_recording_channels,file_path):
 
    with shelve.open(file_path) as shelve_file:
        dataFrame=shelve_file["channel_recordings"]
    new_data=pd.DataFrame({"time":get_current_time(),
                           "total_recording_channels":round(float(total_recording_channels),0),
                           "fail_channel_recordings":round(float(fail_channel_recordings),0)
                           },
                           index=[0])
    logging.debug(f'new_data:\n{new_data}')
    frames=[dataFrame,new_data]
    updatedDataFrame=pd.concat(frames,ignore_index=True)
    with shelve.open(file_path) as shelve_file:
        shelve_file["channel_recordings"]=updatedDataFrame

def create_data_frame_v2(file_path):
    columns=['error_duration', 'last_error_timestamp','channell_name']
    newDataFrame=pd.DataFrame(columns=columns)

    with shelve.open(file_path, flag='n') as shelve_file:
        shelve_file["channel_record_statistic_v2"]=newDataFrame

def is_db_file_exist_v2(host):

    folder_name=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y')))
    file_path=os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_record_statistic_v2'))
    file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_record_statistic_v2'))}.dat"
    
    if sys.platform=='linux':
        file_path_linux=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_record_statistic_v2'))}.db"
    else:
        file_path_windows=f"{os.path.abspath(os.path.join('telemetry',host,datetime.now().strftime('%d-%m-%Y'),'db_channel_record_statistic_v2'))}.dat"
    
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
            create_data_frame_v2file_path)
    else:
        if not os.path.exists(file_path_windows):   # Проверка на существование файла с заданным именем
            logging.debug('creating data_frame file')
            create_data_frame_v2(file_path)

    return folder_name, file_path, file_path_windows

def update_data_frame_v2(host,token,channel_guid,fail_status,file_path):
    current_time=get_current_time()
    with shelve.open(file_path) as shelve_file:
        dataFrame=shelve_file["channel_record_statistic_v2"]
    logging.info(f'channel {channel_guid} fail_status: {fail_status}')
    #Если получен статус ошибки записи то запишем данные в БД timestamp
    
    if fail_status==True:
          
        if channel_guid in dataFrame.index:
            last_error_timestamp=dataFrame.loc[channel_guid, 'last_error_timestamp']
            new_error_duration=current_time-last_error_timestamp
            dataFrame.loc[channel_guid, 'last_error_timestamp']=current_time
            #Если ренее длительности ошибки записи равна 0, то...
            if pd.isna(dataFrame.loc[channel_guid, 'error_duration']):
                dataFrame.loc[channel_guid, 'error_duration']=new_error_duration
            #Если ренее длительности ошибки записи не равна 0, то...
            else:
                error_duration=dataFrame.loc[channel_guid, 'error_duration']
                dataFrame.loc[channel_guid, 'error_duration']=error_duration+new_error_duration
            updatedDataFrame=dataFrame
        else:

            new_data=pd.DataFrame({'last_error_timestamp':current_time,
                                   'channell_name':get_device_name(host,token,channel_guid)},
                                   index=[channel_guid])
            updatedDataFrame=pd.concat([dataFrame,new_data])
        
        with shelve.open(file_path) as shelve_file:
            shelve_file["channel_record_statistic_v2"]=updatedDataFrame



def check_channel_recordings_v3(host):
    while True:
        #Проверка на доступность папки для хранения телеметрии
        _,db_file_path_v1,_=is_db_file_exist_v1(host)
        _,db_file_path_v2,_=is_db_file_exist_v2(host)
        
        #Получить данные о статусах записи каналов сервера
        token=authorization(host)
        data_info=get_channel_recordings(host, token)
        data_info=json.loads(data_info)
        
        #Получим общее количество каналов подлежащих записи
        total_recording_channels=len(data_info["channels"])
        #Посчитаем количество каналов с проблемой получения потока
        fail_channel_recordings=0
        for channel in data_info["channels"]:
            status_info=channel["status"]
            receive_Error=status_info["receiveError"]
            if receive_Error["isError"]==True:
                fail_channel_recordings+=1
        
        logging.info(f'{host}: total_recording_channels={total_recording_channels}, error_count_channells={fail_channel_recordings}')
        update_data_frame_v1(fail_channel_recordings,total_recording_channels,db_file_path_v1)
        
        #Получим статус по каждому каналу
        channel_list=data_info["channels"]
        for channel in channel_list:
            status_info=channel["status"]
            receive_Error=status_info["receiveError"]
            if receive_Error["isError"]==True:
                channel_guid=channel["channel"]
                fail_status=True
                update_data_frame_v2(host,token,channel_guid,fail_status,db_file_path_v2)


        if sys.platform!='linux':
            check_exit_button()
        else:
            pass
        time.sleep(2)


# ------исполняемый код скрипта-------

if __name__ == '__main__':
    _,host=argv
    while True:
        try:
            check_channel_recordings_v3(host)
        except KeyboardInterrupt:    #Без этой строчки код будет выполняться бесконечно при любом количестве ошибок
            logging.info(f' Завершение работы: KeyboardInterrupt')
            is_running=False
            sys.exit(0)
        except Exception as e:
            logging.info(f'ERROR: {e}')
            time.sleep(3)    #Перезапуск процесса скрипта спустя n сек
