from flask import Flask, render_template, request
from sentiment_analyzer import SentimentAnalyzer
import random
from About_the_database import get_db_information
import psycopg2
from psycopg2 import pool

db_config = get_db_information()

app = Flask(__name__)

model_path = './model/'
weights_path = './weights/weights.h5'
data_configs_path = './CLEAN_DATA/data_configs.json'
analyzer = SentimentAnalyzer(model_path, weights_path, data_configs_path)

def get_Unstable_song(): # 불안할때 들을만한 노래 URL 반환
    Unstable_songs = [
        "https://www.youtube.com/embed/tMhizg-1OzA", # 시든 꽃에 물을 주듯 - 박혜원
        "https://www.youtube.com/embed/dyj1C98pZLk", # 돌멩이 - 마씨다밴드
        "https://www.youtube.com/embed/Ibb5RhoKfzE", # 꺼내먹어요 - Zion.T
        "https://www.youtube.com/embed/j4v7OiwNIdk", # 살아가는 거야 - 로이킴
        "https://www.youtube.com/embed/YafkWH9mujo" # 행복은 늘 가까이에 있어 - 볼빨간사춘기
    ]
    return random.choice(Unstable_songs)

def get_Sad_song(): # 슬플때 들을만한 노래 URL 반환
    Sad_songs = [
        "https://www.youtube.com/embed/qGWZUtfV3IU", # Only I didn't know - IU
        "https://www.youtube.com/embed/TDXQEPnwzL0", # 좋은날이 올거야 - 싸이
        "https://www.youtube.com/embed/dY8VsUCRbwU", # 힐링이 필요해 - 로이킴
        "https://www.youtube.com/embed/bkEpWA-4FfU", # 너였다면 - 정승환
        "https://www.youtube.com/embed/tL75qyvHXAs" # 요즘 너말야 - 제이레빗
    ]
    return random.choice(Sad_songs)

def get_Anger_song(): # 화났을때 들을만한 노래 URL 반환
    Anger_songs = [
        "https://www.youtube.com/embed/azaZt7eccnc", # 새삥 - 지코
        "https://www.youtube.com/embed/kJGcO5Une-g", # very good - 블락비
        "https://www.youtube.com/embed/zW9f47Bn6yI", # Don't Touch me - 환불원정대
        "https://www.youtube.com/embed/6GZkDiEqqRY", # 주옥같다 - 고영희
        "https://www.youtube.com/embed/SzyB2xBqkps" # 그건 니 생각이고 - 장기하와 얼굴들
    ]
    return random.choice(Anger_songs)

def get_Happy_song(): # 행복할때 들을만한 노래 URL 반환
    Happy_songs = [
        "https://www.youtube.com/embed/Raj-AuQgCTg", # Happy - 태연
        "https://www.youtube.com/embed/m0o7fbNKhpM", # 상상더하기 - 라붐
        "https://www.youtube.com/embed/DFW81w7aRo0", # 멜로망스 - Happy song
        "https://www.youtube.com/embed/a0iTZZriVME", # 우리 손 놓지 말어 - 호두
        "https://www.youtube.com/embed/uHNvxgotKiw" # 안식 - Normal puppy
    ]
    return random.choice(Happy_songs)

def get_Commonness_song(): # 중립일때 들을만한 노래 URL 반환
    Commonness_songs = [
        "https://www.youtube.com/embed/_tYBbz_RDSI", # 집돌이 - 폴킴
        "https://www.youtube.com/embed/F4K1mMDlsj0", # pet - 10CM
        "https://www.youtube.com/embed/8n9wklIG9qU", # 별 보러 갈래? - 볼빨간사춘기
        "https://www.youtube.com/embed/x2XX3cNW4K0", # Give Love - AKMU
        "https://www.youtube.com/embed/a9X_6IuijP0" # 구름 - 로시
    ]
    return random.choice(Commonness_songs)

def get_Disgust_song(): # 혐오스러울때 들을만한 노래 URL 반환
    Disgust_songs = [
        "https://www.youtube.com/embed/4qOT_Aw9IgM", # 돌덩이 - 하현우
        "https://www.youtube.com/embed/38rUBLSEhw8", # 겁 - 송민호
        "https://www.youtube.com/embed/gluvBLJYBjs", # Shut up - 언니쓰
        "https://www.youtube.com/embed/9DwzBICPhdM", # Not Today - BTS
        "https://www.youtube.com/embed/fagmXQaDjW4" # 1분만 닥쳐줄래요 - 넬
    ]
    return random.choice(Disgust_songs)

# 커넥션 풀 만들기
def create_connection_pool():
    try:
        conn_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return conn_pool
    except (Exception, psycopg2.DatabaseError) as error:
        print("연결이 너무 많습니다.")

conn_pool = create_connection_pool()

# 예측 결과 저장 함수
def save_results(sentence, result, confidence_results):
    conn = conn_pool.getconn()
    cur = conn.cursor()

    # 중복 여부 확인
    duplicate_query = "SELECT id FROM prediction_result WHERE Sentence = %s"
    cur.execute(duplicate_query, (sentence,))
    existing_record = cur.fetchone()

    if not existing_record:
        # 확률 결과 저장
        probability_query = '''INSERT INTO Probability_result(Emotion0, Emotion1, Emotion2, Emotion3, Emotion4, Emotion5)
                               VALUES (%s, %s, %s, %s, %s, %s)
                            '''
        values = (confidence_results['불안'], confidence_results['분노'], confidence_results['슬픔'], confidence_results['중립'], confidence_results['행복'], confidence_results['혐오'])
        cur.execute(probability_query, values)

        # 데이터베이스 변경 사항 커밋
        conn.commit()

        # 예측 결과 저장
        prediction_query = '''INSERT INTO prediction_result(sentence, emotion)
                             VALUES (%s, %s)
                          '''
        cur.execute(prediction_query, (sentence, result))

        emotion_mapping = {
        '불안': 'Unstable',
        '분노': 'Anger',
        '슬픔': 'Sad',
        '중립': 'Commonness',
        '행복': 'Happy',
        '혐오': 'Disgust'
        }
        # 감정 결과 매핑
        if result in emotion_mapping:
            result = emotion_mapping[result]

        # 감정 카운트 업데이트
        update_count_query = "UPDATE emotion_count SET {column} = {column} + 1"
        cur.execute(update_count_query.format(column=result.lower()))
        
        # 데이터베이스 변경 사항 커밋
        conn.commit()

    # 커서 닫기 및 데이터베이스 연결 닫기
    cur.close()
    conn_pool.putconn(conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    sentence = request.form['sentence']
    result, confidence_results = analyzer.predict_sentiment(sentence)
    song_url = None
    if result == '불안':
        song_url = get_Unstable_song()
    elif result == '행복':
        song_url = get_Happy_song()
    elif result == '슬픔':
        song_url = get_Sad_song()
    elif result == '분노':
        song_url = get_Anger_song()
    elif result == '중립':
        song_url = get_Commonness_song()
    else:
        song_url = get_Disgust_song()
    
    save_results(sentence, result, confidence_results)

    # 감정에 따른 노래 함수 호출 및 URL 할당
    return render_template('index.html', result=result, song_url=song_url)

if __name__ == '__main__':
    app.run()