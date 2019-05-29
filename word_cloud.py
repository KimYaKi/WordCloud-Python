# 워드 클라우드 라이브러리
from wordcloud import WordCloud
# 한국어 자연어 처리 라이브러리
from konlpy.tag import Twitter
# 명사의 빈도 출현 카운트 라이브러리
from collections import Counter
# 그래프 생성 라이브러리
import matplotlib.pyplot as plt
# Flask 웹 서버 구축 라이브러리
from flask import Flask, request, jsonify

# 플라스크 웹 서버 객체 생성
app = Flask(__name__)

# 폰트 경로 설정
font_path = 'NanumGothic.ttf'

def get_tags(text, max_count, min_length):
    t = Twitter()
    nouns = t.nouns(text)
    # 단어의 길이가 min_length보다 같거나 클 때만 단어를 저장
    processed = [n for  n in nouns if len(n) >= min_length]
    count = Counter(nouns)
    result = {}

    # 사용 빈도가 높은 (max_count)단어만 사용
    for n, c in count.most_common(max_count):
        result[n] = c
    if len(result) == 0:
        result["내용이 없습니다."] = 1
    return result

# 만들고자 하는 워드 클라우드의 기본 설정을 진행
def make_cloud_image(tags, file_name):
    word_cloud = WordCloud(
        font_path = font_path,
        width = 800,
        height = 800,
        background_color="white"
    )
    # 명사의 빈도수를 출력
    word_cloud = word_cloud.generate_from_frequencies(tags)
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")
    # 만들어진 이미지 객체를 파일 형태로 저장
    fig.savefig("outputs/{0}.png".format(file_name))

# 단어의 최소 길이와 최대 빈도 수 만큼의 단어만 뽑는다
def process_from_text(text, max_count, min_length, words):
    tags = get_tags(text, max_count, min_length)
    # 단어 가중치 적용
    for n, c in words.items():
        if n in tags:
            tags[n] = tags[n] * int(words[n])
    make_cloud_image(tags, "output")

@app.route("/process", methods=['GET', 'POST'])
def process():
    content = request.json
    words = {}
    if content['words'] is not None:
        for data in content['words'].values():
            # words라는 딕셔너리의 word에 따라서 가중치 정보 입력
            words[data['word']] = data['weight']
    # maxCount : 워드클라우드 이미지에 포함 될 최대 단어의 개수
    # minLength : 너무 길이가 짧은 몇몇 단어(단, 즉,)는 제외할 때 사용
    # words : 가중치
    process_from_text(content['text'], content['maxCount'], content['minLength'], words)
    result = {'result':True}
    # words라는 변수를 출력하도록(json)
    return jsonify(words)

if __name__ == '__main__':
    # 5000 port를 이용하여 구동
    app.run('127.0.0.1', port=5000)