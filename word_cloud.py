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
# 테스트를 위하여 CORS를 처리합니다.
from flask_cors import CORS
# 파일에 접근하기 위한 라이브러리를 불러옵니다.
import os

# 플라스크 웹 서버 객체 생성
app = Flask(__name__, static_folder='outputs')
CORS(app)

# 폰트 경로 설정
font_path = 'NanumGothic.ttf'

def get_tags(text, max_count, min_length):
    # 명사 추출
    t = Twitter()
    nouns = t.nouns(text)
    # 단어의 길이가 min_length 보다 같거나 클 때만 단어를 저장
    processed = [n for n in nouns if len(n) >= min_length]
    # 모든 명사의 출현 빈도를 계산
    count = Counter(processed)
    result = {}

    # 사용 빈도가 높은 max_count 개의 명사 단어만 사용
    for n, c in count.most_common(max_count):
        result[n] = c

    # 추출된 단어가 하나도 없는 경우 "내용이 없습니다"출력
    if len(result) == 0:
        result["내용이 없습니다."] = 1
    return result

# 만들고자 하는 워드 클라우드의 기본 설정을 진행
def make_cloud_image(tags, file_name):
    word_cloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color="white"
    )
    # 명사의 빈도수를 출력
    word_cloud = word_cloud.generate_from_frequencies(tags)
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")

    path = "outputs/{0}.png".format(file_name)
    # 이미 만들어진 파일이 존재하는 경우 덮어쓰기
    if os.path.isfile(path):
        os.remove(path)
    # 만들어진 이미지 객체를 파일 형태로 저장
    fig.savefig(path)

# 단어의 최소 길이와 최대 빈도 수 만큼의 단어만 뽑는다
def process_from_text(text, max_count, min_length, words, file_name):
    tags = get_tags(text, max_count, min_length)
    # 단어 가중치 적용
    for n, c in words.items():
        if n in tags:
            tags[n] = tags[n] * int(words[n])
    # 명사의 출현 빈도 정보를 통해 워드 클라우드 이미지 생성
    make_cloud_image(tags, file_name)

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
    process_from_text(content['text'], content['maxCount'], content['minLength'], words, content['textID'])
    result = {'result': True}
    # words라는 변수를 출력하도록(json)
    return jsonify(result)

# 이미지 출력을 위한 함수
@app.route('/outputs', methods=['GET', 'POST'])
def output():
    text_id = request.args.get('textID')
    return app.send_static_file(text_id + '.png')

# 이미지 존재 여부 확인을 위한 validate()함수
@app.route('/validate',methods=['GET','POST'])
def validate():
    text_id = request.args.get("textID")
    path = "outputs/{0}.png".format(text_id)
    result = {}
    if os.path.isfile(path):
        result['result'] = True
    else:
        result['result'] = False
    return jsonify(result)

if __name__ == '__main__':
    # 5000 port를 이용하여 구동
    # 처리 속도 향상을 위한 스레드 적용
    app.run('127.0.0.1', port=5000, threaded=True)