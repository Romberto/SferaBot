import datetime

from database.config_db import connect
from collections import namedtuple

Token = namedtuple('Token', [
    'id', 'active', 'body', 'date_create', 'date_activate', 'driver_activate', 'excursion_name', 'excursion_price'
])


async def get_token(token_text: str):
    conn = connect()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT tokens_tokenexmodel.id, tokens_tokenexmodel.active,"
                           "tokens_tokenexmodel.body,tokens_tokenexmodel.date_create,"
                           "tokens_tokenexmodel.date_activate,tokens_tokenexmodel.driver_activate_id"
                           ", excursions_excursionmodel.name, excursions_excursionmodel.price "
                           "FROM tokens_tokenexmodel RIGHT JOIN excursions_excursionmodel "
                           "ON tokens_tokenexmodel.excursion_id = excursions_excursionmodel.id WHERE "
                           "body='" + token_text + "' AND active = 'True'")
            record = cursor.fetchone()
            token_db = Token(
                id=record[0],
                active=record[1],
                body=record[2],
                date_create=record[3],
                date_activate=record[4],
                driver_activate=record[5],
                excursion_name=record[6],
                excursion_price=record[7]
            )
            cursor.close()
            return token_db
        except Exception as _err:
            print('token_db.py => get_token', _err)
            return False
        finally:
            conn.close()
    else:
        print("проблемы с подключением к базе")

async def token_finaly(token:str, driver):
    conn = connect()
    if conn:
        today = datetime.datetime.now()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE tokens_tokenexmodel SET active='False', date_activate='"+today.strftime('%Y-%m-%d %H:%M:%S')+"', driver_activate_id='16' WHERE body='"+token+"';")
            conn.commit()
            cursor.close()
        except Exception as _err:
            print('token_db.py => token_finaly', _err)
            return False
        finally:
            conn.close()
    else:
        print("проблемы с подключением к базе")