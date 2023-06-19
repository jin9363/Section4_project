import re
import json
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model
import numpy as np

class SentimentAnalyzer:
    def __init__(self, model_path, weights_path, data_configs_path):
        self.okt = Okt()
        self.tokenizer = Tokenizer()
        self.load_data_configs(data_configs_path)
        self.load_model(model_path, weights_path)
        self.class_labels = ['불안', '분노', '슬픔', '중립', '행복', '혐오']
        self.max_length = 30

    def load_data_configs(self, data_configs_path):
        prepro_configs = json.load(open(data_configs_path, 'r'))
        word_vocab = prepro_configs['vocab']
        self.tokenizer.fit_on_texts(word_vocab)

    def load_model(self, model_path, weights_path):
        self.model = load_model(model_path)
        self.model.load_weights(weights_path)

    def preprocess_sentence(self, sentence):
        sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]', '', sentence)
        stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등', '한']
        sentence = self.okt.morphs(sentence, stem=True)
        sentence = [word for word in sentence if not word in stopwords]
        vector = self.tokenizer.texts_to_sequences([sentence])  # 문장을 리스트로 감싸서 전달
        pad_new = pad_sequences(vector, maxlen=self.max_length)
        return pad_new

    def predict_sentiment(self, sentence):
        preprocessed_sentence = self.preprocess_sentence(sentence)
        predictions = self.model.predict(preprocessed_sentence)
        max_index = np.argmax(predictions[0])
        class_name = self.class_labels[max_index]
        confidence_results = {}

        for i, label in enumerate(self.class_labels):
            confidence = round(float(predictions[0, i]), 2)
            confidence_results[label] = confidence
        return class_name, confidence_results