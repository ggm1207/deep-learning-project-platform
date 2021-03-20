# -*- coding: utf-8 -*-
"""Latent_Vector_Collaborative_Recommend_forServer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15QsNrUfOFlIBW_rCJoE399hayVUqN3XX
"""

from sklearn.decomposition import TruncatedSVD
from scipy.sparse.linalg import svds

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import os, sys 
from google.colab import drive 

### 해당 코드 실행 시 colab에서 실행중인 폴더의 /content/drive/My Drive가 구글 드라이브에 연결됨

drive.mount('/content/drive')

# 데이터셋 불러오기(MovieLens 100k)
rating_data = pd.read_csv('drive/MyDrive/data/others/ratings.csv')

# 평점 데이터셋 형태 확인
print("### Rating Dataset Format ###", end='\n\n')
print(rating_data.head(), end='\n\n\n')
rating_data.drop(['timestamp'], axis=1, inplace=True)


movie_data = pd.read_csv('drive/MyDrive/data/others/movies.csv')

# 영화 데이터셋 형태 확인
print("### Movie Dataset Format ###", end = '\n\n')
print("Columns of Movie Dataset : ",movie_data.columns, end = '\n\n')
print(movie_data.head())

print(movie_data.shape)
print(rating_data.shape)

movie_data.drop('genres', axis = 1, inplace = True)

user_movie_data = pd.merge(rating_data, movie_data, on = 'movieId')
user_movie_data.head()

user_movie_data.shape

user_movie_rating = user_movie_data.pivot_table('rating', index = 'userId', columns='title').fillna(0)

user_movie_rating.shape

user_movie_rating.head()

movie_user_rating = user_movie_rating.values.T
movie_user_rating.shape

type(movie_user_rating)

SVD = TruncatedSVD(n_components=12)
matrix = SVD.fit_transform(movie_user_rating)
matrix.shape

matrix[0]

corr = np.corrcoef(matrix)
corr.shape

corr2 = corr[:200, :200]
corr2.shape

plt.figure(figsize=(16, 10))
sns.heatmap(corr2)

def get_recommend_movie_list(movie_name, top=20):
    # 특정 영화와 비슷한 영화를 추천해야 하기 때문에 '특정 영화' 정보를 뽑아낸다.
    
    movie_title = user_movie_rating.columns
    movie_title_list = list(movie_title)
    coffey_hands = movie_title_list.index(movie_name)
    corr_coffey_hands = corr[coffey_hands]
    #본인을 제외, Score 순으로 Sort, 역순으로 뒤집기
    corr_coffey_hands = corr_coffey_hands.argsort()[:-1][::-1]
    
    #list으로 만들고 top 개수만큰 뽑아준 뒤 return
    result = list(movie_title[corr_coffey_hands])[:top]
    result = [x.split(' (')[0] for x in result]
    return result

rec2 = get_recommend_movie_list('Avatar (2009)')
rec2

from pandas import DataFrame
df = DataFrame(rec2,columns=['title'])
df

import requests
from urllib.request import urlopen
from PIL import Image

def movie_poster(titles):
    data_URL = 'http://www.omdbapi.com/?i=tt3896198&apikey=f9cdaffd'
    
    fig, axes = plt.subplots(2, 10, figsize=(30,9))
    
    for i, ax in enumerate(axes.flatten()):
        w_title = titles[i].strip().split()
        params = {
            's':titles[i],
            'type':'movie',
            'y':''    
        }
        response = requests.get(data_URL,params=params).json()
        
        if response["Response"] == 'True':
            poster_URL = response["Search"][0]["Poster"]
            img = Image.open(urlopen(poster_URL))
            ax.imshow(img)
            
        ax.axis("off")
        if len(w_title) >= 10:
            ax.set_title(f"{i+1}. {' '.join(w_title[:5])}\n{' '.join(w_title[5:10])}\n{' '.join(w_title[10:])}", fontsize=10)
        elif len(w_title) >= 5:
            ax.set_title(f"{i+1}. {' '.join(w_title[:5])}\n{' '.join(w_title[5:])}", fontsize=10)
        else:
            ax.set_title(f"{i+1}. {titles[i]}", fontsize=10)
        
    plt.show()

movie_poster(rec2)

!pip install flask_cors

!pip install flask-ngrok

import io
from flask_ngrok import run_with_ngrok
from flask import Flask, jsonify, request
from PIL import Image
from flask_cors import CORS, cross_origin
import os
import json

# 이미지를 읽어 결과를 반환하는 함수
def get_prediction(title):
    rec2 = get_recommend_movie_list(title)
    rec2 = DataFrame(rec2,columns=['title'])
    rec2 = rec2['title'].apply(lambda x : x.split(' (')[0]) # 이부분 필요없음. 근데 dataframe에서 apply 해줘야 [[],[]] 형태가 안생김. 이유는 모르겠음
    return rec2.to_json(orient="split")


app = Flask(__name__)
CORS(app)

@app.route('/post', methods=['POST'])
def predict():
    content = request.get_json(force=True, silent=True)
    print("title:", content['title'])
    title=content['title']
    year=content['year']
    input = title+' ('+year+')'
    print("input", input)
    #processing title


    if request.method == 'POST':    
        #받은 데이터 처리
        res = get_prediction(input)
        print("결과:", res)
        return jsonify(res)

run_with_ngrok(app)
app.run()






