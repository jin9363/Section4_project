import pandas as pd
import psycopg2
from About_the_database import get_db_information
import json
from psycopg2.extras import execute_values

# 데이터베이스 연결 설정
db_config = get_db_information()

conn = psycopg2.connect(host = db_config['host'],
                        port = db_config['port'],
                        database = db_config['database'],
                        user = db_config['user'],
                        password = db_config['password'])
cur = conn.cursor()

# 모델링에 사용된 데이터 데이터베이스 저장 -> 저장 다하고 주석처리해놓음

# create_table = '''CREATE TABLE IF NOT EXISTS model_file(
#                     Sentence VARCHAR(400) NOT NULL,
#                     Emotion VARCHAR(10) NOT NULL
# )
# '''

# cur.execute(create_table)

# data = pd.read_excel('./model_file.xlsx')

# insert_data = '''INSERT INTO model_file(Sentence, Emotion)
#                     VALUES (%s, %s)
# '''

# values = []

# for row in data.itertuples(index=False):
#     values.append(row)

# cur.executemany(insert_data, values)

# conn.commit()
# cur.close()
# conn.close()

create_Probability_table = '''CREATE TABLE IF NOT EXISTS Probability_result(
                    id SERIAL PRIMARY KEY,
                    Emotion0 FLOAT NOT NULL,
                    Emotion1 FLOAT NOT NULL,
                    Emotion2 FLOAT NOT NULL,
                    Emotion3 FLOAT NOT NULL,
                    Emotion4 FLOAT NOT NULL,
                    Emotion5 FLOAT NOT NULL
)
'''
cur.execute(create_Probability_table)
conn.commit()

create_table = '''CREATE TABLE IF NOT EXISTS prediction_result(
                    id SERIAL PRIMARY KEY,
                    Sentence TEXT NOT NULL,
                    Emotion TEXT NOT NULL,
                    Probability_id SERIAL,
                    FOREIGN KEY (Probability_id) REFERENCES Probability_result(id)
)
'''
cur.execute(create_table)

conn.commit()
# cur.close()
# conn.close()

# 입력값을 받아 감정분류로 나온 감정 count하는 table
create_table = '''
    CREATE TABLE IF NOT EXISTS emotion_count (
        id SERIAL PRIMARY KEY,
        Unstable INT DEFAULT 0,
        Anger INT DEFAULT 0,
        Sad INT DEFAULT 0,
        Commonness INT DEFAULT 0,
        Happy INT DEFAULT 0,
        Disgust INT DEFAULT 0
    )
'''

insert_query = '''
    INSERT INTO emotion_count (Unstable, Anger, Sad, Commonness, Happy, Disgust)
    VALUES (%(불안)s, %(분노)s, %(슬픔)s, %(중립)s, %(행복)s, %(혐오)s)
    ON CONFLICT (id) DO NOTHING
'''

emotion_count = {
    '불안': 0,
    '분노': 0,
    '슬픔': 0,
    '중립': 0,
    '행복': 0,
    '혐오': 0
}

cur.execute(create_table)
cur.execute(insert_query, emotion_count)
conn.commit()
cur.close()
conn.close()