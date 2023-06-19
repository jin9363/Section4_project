import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

url = 'https://www.100ssd.co.kr/news/articleView.html?idxno=84282'

sample = requests.get(url)

soup = BeautifulSoup(sample.content, 'html.parser')

page = soup.find(id='article-view-content-div')
p_tags = soup.find_all('p')

# 추출할 시작과 끝을 나타내는 키워드
start_keyword = "루이보스"
end_keyword = "허브차 블렌딩 방법"

# 시작과 끝 키워드가 포함된 <p> 태그 추출
start_tag = None
end_tag = None

for p in p_tags:
    if start_keyword in p.text:
        start_tag = p
    elif end_keyword in p.text:
        end_tag = p
        break

# 시작과 끝 태그 사이의 데이터 출력
if start_tag and end_tag:
    start_index = p_tags.index(start_tag)
    end_index = p_tags.index(end_tag)
    for p in p_tags[start_index:end_index]:
        print(p.text)