# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 14:13:55 2022

@author: Юрий
"""
import sqlalchemy
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from config import Config

import logging
#logging.basicConfig(filename='back.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import datetime

################ БЛОК ИНИЦИАЛИЗАЦИИ
config = Config()

DATABASE = config.get_db_conf()

print(URL(**DATABASE))

engine = create_engine(URL(**DATABASE), echo=False)
if engine:
    logging.info('DB is connected')
else:
    logging.critical('Can not connect to DB!')

Base = declarative_base()
metadata = MetaData(bind=engine)

#Это большая исходная таблица для запросов доп-инфо
class GrandTable(Base): 
    __table__ = Table('full_table', metadata, autoload=True)  
    __mapper_args__ = {'primary_key': [__table__.c.root_request_id]} 

#Это сокращенная таблица, содержащая только основную инфо
class ZKH(Base): 
    __table__ = Table('search_data', metadata, autoload=True)  
    __mapper_args__ = {'primary_key': [__table__.c.root_request_id]} 

#Это таблица с настроениями людей
class MoodData(Base): 
    __table__ = Table('mood_data', metadata, autoload=True)  
    __mapper_args__ = {'primary_key': [__table__.c.root_request_id]} 
    

def get_session():
    """
    get_session creates engine and session based on provided database location.
    
    :return: session for queries to DB
    """ 
    engine = create_engine(URL(**DATABASE), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    logging.debug('Send session connection to flask')
    return session

################################################################   
    
##################### БЛОК РАБОТЫ С НАСТРОЕНИЕМ ##################

def get_full_mood(session, start='2021-01-01', finish='2022-01-01'):
    """
    get_full_mood получает список настроений с координатами
    
    :param session: подключение к БД
    :param start: фильтр по датам - левая граница
    :param finish: фильтр по датам - правая граница
    :return: номер заявки, номер настроения, дата заявки, координаты
    """
    logging.debug('Getting mood list for heatmap page')
    statement = select([MoodData.root_request_id, MoodData.mood_id,
                        MoodData.created_ts, MoodData.latitude, MoodData.longitude]).where((MoodData.created_ts>=start) & (MoodData.created_ts<=finish) & (MoodData.mood_id==2))
    try:
        result = session.execute(statement)  
        return result
    except:
        logging.error('Error reading from DB, rolling back...')
        session.rollback()
        raise

def json_mood_data_template(root_request_id, mood_id, created_ts, latitude, longitude):
    """
    json_mood_data_template - шаблон json файла, который будет отправлен в карту
    
    :param root_request_id: id заявки
    :param mood_id: id настроения
    :param created_ts: дата создания заявки
    :param latitude,longitude: координаты адреса заявки
    :return: json-строку
    """
    logging.debug('Received list to jsonify')
    return {
        "global_id": root_request_id,
        "mood_id": mood_id,
        "created_ts": created_ts,
        "geoData": {"type": "Point", "coordinates": [float(latitude), float(longitude)]}
}
    
   
def send_mood_map(session, mood_map):
    """
    send_mood_map - получает сырые данные из ДБ и с помощью шаблона приводит их в json
    
    :param session: подключение к БД
    :param mood_map: сырые данные из БД
    :return: json файл, отправляемый в карту
    """    
    logging.debug('received request for mood map')
    mood_data = []
    for i in mood_map:
        mood_data.append(json_mood_data_template(i.root_request_id, i.mood_id, i.created_ts, i.latitude,
                                               i.longitude))
    return(mood_data)
    

###############################################################

############## БЛОК РАБОТЫ СО СТРАНИЦЕЙ БД
def get_address_list(session):
    """
    get_address_list получает сессию и делает запрос к БД для наполнения онлайн-отображения таблицы
    
    :param session: подключение к БД
    :return: строки id, адрес, координаты и имя дефекта из сокращенной таблицы
    """ 
    logging.info('Getting address list for DB page')
    statement = select([ZKH.root_request_id, ZKH.problem_address,
                        ZKH.address_lat, ZKH.address_long, ZKH.defect_cat_name]).limit(50)
    try:
        result = session.execute(statement)  
        return result
    except:
        logging.error('Error reading from DB, rolling back...')
        session.rollback()
        raise


def close_connection(session):
    """
    close_connection закрывает все соединения к БД
    
    :param session: подключение к БД
    """
    engine = session.get_bind()
    engine.dispose() 


#########################################################
    
############## Блок получения дополнительной инфорации и передачи ее в карту ############

def json_add_data_template(root_request_id, effectiveness, management_comp_name, job_type, description, request_num, defect_cat_name,
                           defect_name, created_ts, closed_date, data_source_name, comments, payment_cat_name,
                           rule_one, rule_two, rule_three, rule_four, rule_five):
    """
    json_add_data_template используется для форматирования параметров в словарик, понятный карте
    
    :param root_request_id: id проблемы 
    :param description: описание проблемы, выгруженной из большой БД
    :return: словарик, понятный карте
    """ 
    problem=[]
    if rule_one:
        problem.append('Закрыто без выполнения')
    if rule_two:
        problem.append('Последовательные заявки на одну тему')
    if rule_three:
        problem.append('Повторное обращение после быстрого выполнения')
    if rule_four:
        problem.append('Закрыто быстрее, чем физически возможно выполнить')
    if rule_five:
        problem.append('Возврат на доработку')
    if len(problem) > 0:
        problems = ','.join(problem)
        problems =  f"<font color=#CC0000>{problems}</font>"
    else:
        problems = 'Проблем не обнаружено'

    return {'id':root_request_id, 
            'balloonContentHeader':f'<b>Номер заявки:</b> {request_num}<br><b>Категория дефекта:</b> {defect_cat_name}',
            'balloonContentBody': f'<b>Проблема:</b> {defect_name}<br><b>Выполненные работы:</b> {job_type}<br><b>Результативность:</b> {effectiveness}<br><b>Управляющая компания:</b> {management_comp_name}',
            'balloonContentFooter': f'<b>Создано:</b> {created_ts}<br><b>Закрыто:</b> {closed_date}<br>{problems}',
            'balloonAdditional':f'<b>Описание:</b> {description}<br><b>Источник заявки:</b> {data_source_name}<br><b>Комментарий:</b> {comments}<br><b>Тип оплаты:</b> {payment_cat_name}'
            }

def get_add_data(session, ids):
    """
    get_add_data получает список id и отправляет запрос в БД для получения по ним допинфо
    
    :param session: подключение к БД
    :param ids: список айдишников заявок
    :return: дополнительная информация в виде списка словариков
    """ 
    add_data = []
    logging.debug('Received ids list for DB query for additional info', ids)
    statement = select([GrandTable.root_request_id, GrandTable.effectiveness, GrandTable.management_comp_name, GrandTable.job_type,
                        GrandTable.description, GrandTable.request_num, GrandTable.defect_cat_name,
                        GrandTable.defect_name, GrandTable.created_ts, GrandTable.closed_date, GrandTable.data_source_name,
                        GrandTable.comments, GrandTable.payment_cat_name, GrandTable.rule_one, GrandTable.rule_two,
                        GrandTable.rule_three, GrandTable.rule_four, GrandTable.rule_five
                        ]).where(GrandTable.root_request_id.in_(ids))
    
    try:
        result = session.execute(statement)
    except:
        logging.error('Error reading from DB, rolling back...')
        session.rollback()
        raise
    for i in result:
        add_data.append(json_add_data_template(i.root_request_id, i.effectiveness, i.management_comp_name, i.job_type,
                                               i.description, i.request_num, i.defect_cat_name, i.defect_name,
                                               i.created_ts, i.closed_date, i.data_source_name, i.comments, i.payment_cat_name,
                                               i.rule_one, i.rule_two, i.rule_three, i.rule_four, i.rule_five))
    logging.debug('Got additional info from DB')
    return add_data  


#################################################################################
        
################# Блок для загрузки меток, видимых на экране #############################
def json_line_template(problem_id, request_num, coords_lat, coords_long, problem_address, is_problem_flg):
    """
    json_line_template - шаблон словарика, содержащего информацию о метке

    :param problem_id: id проблемы
    :param coords_lat: широта
    :param coords_long: долгота
    :param problem_address: адрес
    :param defect_cat_name: категория проблемы

    :return: словарик с информацией об одной метке
    """ 
    if is_problem_flg:
        hasProblem = 'Заявки с проблемами'
        color = "islands#redCircleDotIconWithCaption"
        border_color = '#f50505'
        request_num = f"<div style=\"color:#CC0000\">{request_num}</div>"
    else:
        hasProblem = 'Заявки без проблем'
        color = "islands#blueCircleDotIconWithCaption"
        border_color = '#000000'
        
    return {'type': 'Feature',
            'id': problem_id,
            'geometry': {'type': 'Point', 'coordinates': [coords_lat, coords_long]},
            'properties': {'balloonContentBody': 'идет загрузка...',
                           'clusterCaption': request_num,
                           'hintContent': problem_address,
                           "hasProblem":hasProblem,
                            "border_color":border_color},
                            "options": {"preset": color}
                            }
     
def get_bboxed_data(session, bbox, problem_types, start_time=datetime.date(2021,1,1), finish_time=datetime.date(2021,1,5), searchline=None, isproblem='all'):
    """
    get_bboxed_data получает координаты видимой в данный момент на экране области и получает из БД метки, лежащие в этой области

    :param session: подключение к БД
    :param bbox: список координат: координаты левого нижнего и правого верхнего углов области.
    :param problem_types: список типов работ по заявкам
    :param start_time, finish_time : время, в рамках которого должна была быть создана завяка
    :param searchline: поисковый запрос по номеру заявки
    :param isproblem: all, True или False - тип меток, о которых требуется выгружать информацию, с проблемами или без  
    :return: полученный из БД сырая информация о метках
    """ 

    logging.info('Query DB marks in bbox')
    if isproblem=='None':
         statement = select([ZKH.root_request_id, ZKH.problem_address, ZKH.request_num,
                             ZKH.address_lat, ZKH.address_long, ZKH.is_problem_flg]).where(1==0)
    elif isproblem=='all':
        if searchline:
            statement = select([ZKH.root_request_id, ZKH.problem_address, ZKH.request_num,
                                ZKH.address_lat, ZKH.address_long, ZKH.is_problem_flg]).where(
                                    (ZKH.address_lat>bbox[0]) & (ZKH.address_lat<bbox[2]) & (ZKH.address_long>bbox[1]) & (ZKH.address_long<bbox[3]) & (ZKH.created_ts>=start_time)  & (ZKH.created_ts<=finish_time)
                                    & (ZKH.defect_cat_root_id.in_(problem_types))  & (ZKH.request_num.like('%' + searchline + '%'))
                                    )
        else: 
            statement = select([ZKH.root_request_id, ZKH.problem_address, ZKH.request_num,
                                ZKH.address_lat, ZKH.address_long, ZKH.is_problem_flg]).where(
                                    (ZKH.address_lat>bbox[0]) & (ZKH.address_lat<bbox[2]) & (ZKH.address_long>bbox[1]) & (ZKH.address_long<bbox[3]) & (ZKH.created_ts>=start_time)  & (ZKH.created_ts<=finish_time)
                                    & (ZKH.defect_cat_root_id.in_(problem_types))
                                   )
    else:
        if searchline:
            statement = select([ZKH.root_request_id, ZKH.problem_address, ZKH.request_num,
                                ZKH.address_lat, ZKH.address_long, ZKH.is_problem_flg]).where(
                                    (ZKH.address_lat>bbox[0]) & (ZKH.address_lat<bbox[2]) & (ZKH.address_long>bbox[1]) & (ZKH.address_long<bbox[3]) & (ZKH.created_ts>=start_time)  & (ZKH.created_ts<=finish_time)
                                    & (ZKH.defect_cat_root_id.in_(problem_types))  & (ZKH.request_num.like('%' + searchline + '%')) & (ZKH.is_problem_flg == isproblem)
                                    )   
        else: 

            statement = select([ZKH.root_request_id, ZKH.problem_address, ZKH.request_num,
                                ZKH.address_lat, ZKH.address_long, ZKH.is_problem_flg]).where(
                                    (ZKH.address_lat>bbox[0]) & (ZKH.address_lat<bbox[2]) & (ZKH.address_long>bbox[1]) & (ZKH.address_long<bbox[3]) & (ZKH.created_ts>=start_time)  & (ZKH.created_ts<=finish_time)
                                    & (ZKH.defect_cat_root_id.in_(problem_types)) & (ZKH.is_problem_flg==isproblem)
                                    )        
    try:
        result = session.execute(statement)  
        return result
    except:
        logging.error('Error reading from DB, rolling back...')
        session.rollback()
        raise

def from_db_to_dict_bbox(session, items):
    """
    from_db_to_dict_bbox получает информацию о метках и создает словарик для последующей отправки в карту

    :param session: подключение к БД
    :param items: сырая информация по меткам в видимой области
    :return: словарик в формате, понятным карте
    """ 

    list_to_append = []
    for item in items:
        list_to_append.append((json_line_template(item.root_request_id, item.request_num, float(item.address_lat), 
                                                  float(item.address_long), item.problem_address,
                                                  item.is_problem_flg))) 
    if not list_to_append:
        logging.warning('No marks found in bbox')
    else:
        logging.debug('Found marks in bbox: ', len(list_to_append))
    return {"type": "FeatureCollection", "features":list_to_append}

#####################################################################################   