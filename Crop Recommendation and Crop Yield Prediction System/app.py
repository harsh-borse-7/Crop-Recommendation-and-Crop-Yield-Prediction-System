from flask import Flask, render_template,request,redirect
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app=Flask(__name__)
cors=CORS(app)

with open("Crop_recommendation.pickle",'rb') as f:
    model_recomm=pickle.load(f)
with open("Yield_prediction.pickle",'rb') as f:
    model_yield=pickle.load(f)
with open('labelencoder.pickle','rb') as f:
    label=pickle.load(f)

csv_yeild=pd.read_csv("Final_csv.csv")
csv_recom=pd.read_csv("labelencoded.csv")
csv_state_names=pd.read_csv('Crop_yield.csv')

len_state= len(sorted(csv_state_names['State_Name'].unique()))

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reccom',methods=['GET'])
def reccom():
    return render_template('reccom.html')

@app.route('/yield',methods=['GET'])
def yield1():
    states = sorted(csv_state_names['State_Name'].unique())
    print("hello")
    print(states)
    print(len(states))
    return render_template('yield.html',states=states)


@app.route('/reccom',methods=['POST'])
@cross_origin()
def reccomend():
    N=request.form.get('n')
    P=request.form.get('p')
    K=request.form.get('k')
    temperature=request.form.get('temp')
    humidity=request.form.get('humidity')
    ph=request.form.get('ph')
    rainfall=request.form.get('rainfall')

    value2=model_recomm.predict([[N,P,K,temperature,humidity,ph,rainfall]])

    suggest=label.inverse_transform(value2)
    print(suggest)
    return str(suggest[0])

@app.route('/yield',methods=['POST'])
@cross_origin()
def yield_pred():

    area=request.form.get('area')
    year=request.form.get('year')
    rainfall=request.form.get('rainfall')
    select_state=request.form.get('select_state')

    last_of_list=((sorted(csv_state_names['State_Name'].unique()))[-1])

    if (select_state ==(last_of_list)):
        x = np.zeros(len_state + 2)

        x[0] = year
        x[1] = area
        x[2] = rainfall
    else:
        loc_index = np.where(csv_yeild.columns == select_state)[0][0]

        x = np.zeros(len_state+2)

        loc_index=loc_index-1
        x[0] = year
        x[1] =area
        x[2] = rainfall
        if loc_index >= 0:
            x[loc_index] = 1

    pred=model_yield.predict([x])[0]
    return str(round(float(pred) / float(area),2))


if __name__=='__main__':
    app.run(debug=True)

