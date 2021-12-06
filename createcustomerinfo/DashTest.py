import os.path
import yaml
import random
import datetime
from sqlalchemy import text, create_engine, MetaData, select
from sqlalchemy import Table, Column, String, Float, Integer
from sqlalchemy.orm import registry, Session
from sqlalchemy.orm import declarative_base
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

yamlfilepath = os.path.expanduser('~\\yamlfiles\\information.yaml') 
with open(yamlfilepath) as f:
    login = yaml.load(f, Loader=yaml.FullLoader)

address = f'postgresql://{login["user"]}:{login["pw"]}@localhost:{login["port"]}/{login["db"]}'
engine = create_engine(address)
metadata_obj = MetaData()
Base = declarative_base()


age = Table(
    "age",
    metadata_obj,
    Column('age', String(30), primary_key=True), 
    Column('rate', Float)
)

resion = Table(
    "resion",
    metadata_obj,
    Column('resion', String(30), primary_key=True), 
    Column('rate', Float)
)

sex = Table(
    "sex",
    metadata_obj,
    Column('sex', String(30), primary_key=True), 
    Column('rate', Float)
)

lastname = Table(
    "lastname",
    metadata_obj,
    Column('lastname', String(30), primary_key=True), 
    Column('rate', Float)
)

firstname = Table(
    "firstname",
    metadata_obj,
    Column('firstname', String(30), primary_key=True), 
    Column('rate', Float)
)
zero = Table(
    "zero",
    metadata_obj,
    Column('zero', String(30), primary_key=True), 
    Column('rate', Float)
)
class Age(Base):
    __tablename__ = 'age'
    age = Column(String(30), primary_key=True)
    rate = Column(Float)
    
    def __repr__(self):
        return f"{self.age!r},{self.rate!r}"
    
class Resion(Base):
    __tablename__ = 'resion'
    resion = Column(String(30), primary_key=True)
    rate = Column(Float)
    
    def __repr__(self):
        return f"{self.resion!r},{self.rate!r}"
    
class Sex(Base):
    __tablename__ = 'sex'
    sex = Column(String(30), primary_key=True)
    rate = Column(Float)
    
    def __repr__(self):
        return f"{self.sex!r},{self.rate!r}"
    
class LastName(Base):
    __tablename__ = 'lastname'
    lastname = Column(String(30), primary_key=True)
    rate = Column(Float)
    
    def __repr__(self):
        return f"{self.lastname!r},{self.rate!r}"
    
class FirstName(Base):
    __tablename__ = 'firstname'
    firstname = Column(String(30), primary_key=True)
    rate = Column(Float)
    
    def __repr__(self):
        return f"{self.firstname!r},{self.rate!r}"
class Zero(Base):
    __tablename__ = 'zero'
    zero = Column(String(30), primary_key=True)
    rate = Column(Float)
    
customer = Table(
    "customer",
    metadata_obj,
    Column('cid', Integer, primary_key=True),
    Column('lastname', String(30)), 
    Column('firstname', String(30)),
    Column('sex', String(30)),
    Column('dateofbirth', String(30)),
    Column('subdate', String(30))
)
class Customer(Base):
    __tablename__ = 'customer'
    
    cid = Column(Integer, primary_key=True)
    lastname = Column(String(30))
    firstname = Column(String(30))
    sex = Column(String(30))
    dateofbirth = Column(String(30))
    subdate = Column(String(30))
    
    def __repr__(self):
        return f"{self.lastname!r},{self.firstname!r},{self.sex!r},{self.dateofbirth!r},{self.subdate!r}"


metadata_obj.create_all(engine)

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash import callback_context

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1(children='Hello Dash'),
    
    html.Div(children='''
        Choice it to see the graph of rate.
    '''),
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': i, 'value': i}
            for i in ['성별 비율', '성 비율', '이름 비율', '나이 비율']
        ],
        value='성별 비율'
    ),
    
    dcc.Graph(id='dd-output-container'),
   
    html.Button("비교하기", id="btn-bongraph", n_clicks=0),
    dcc.Graph(id="bongraph") 

])

@app.callback(
    Output('dd-output-container', 'figure'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    if value =='성별 비율':
        df = pd.read_sql(select(Customer), engine)
        dfsex = df.groupby(['sex'], as_index=False).count()
        dffig = dfsex.assign(rate = dfsex.cid.transform(func = lambda x : x / len(df.index)))
        fig = px.pie(dffig, values='rate', names='sex', color='sex', title='고객 테이블 성별')
    
    elif value =='성 비율':
        df = pd.read_sql(select(Customer), engine)
        dflast = df.groupby(['lastname'], as_index=False).count()
        dffig = dflast.assign(rate = dflast.cid.transform(func = lambda x : x / len(df.index)))
        dffig = dffig.sort_values(by='rate' ,ascending=False).head(30)
        fig = px.bar(dffig, x="lastname", y="rate", title='고객 테이블 성(姓) 상위 30개 ', color='rate', labels={'rate': '비율(%)', 'lastname':'성(姓)'})
        
    
    elif value =='이름 비율':
        df = pd.read_sql(select(Customer), engine)
        dffir = df.groupby(['firstname'], as_index=False).count()
        dffig = dffir.assign(rate = dffir.cid.transform(func = lambda x : x / len(df.index)))
        dffig = dffig.sort_values(by='rate' ,ascending=False).head(15)
        labelss = dffig['firstname']
        valuess = dffig['rate']
        fig = go.Figure(data=[go.Pie(labels=labelss, values=valuess, hole=.3)],\
                     layout=go.Layout(title=go.layout.Title(text="이름")))
    
    elif value =='나이 비율':
        df = pd.read_sql(select(Customer), engine)
        df = df.assign(year = df['dateofbirth'].str[:4])
        dfdate = df.groupby(['year'], as_index=False).count()
        dffig = dfdate.assign(rate = dfdate.cid.transform(func = lambda x : x / len(df.index)))
        fig = px.scatter(dffig, x="year", y="rate", title='고객 테이블 생년월일', color='rate', labels={'rate': '비율(%)', 'age': '나이(세)'})
    
    return fig



@app.callback(
    Output('bongraph', 'figure'),
    Input('btn-bongraph', 'n_clicks'),
    Input('demo-dropdown', 'value')
)
def update_output(n_clicks, value):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if value =='성별 비율' and ('btn-bongraph' in changed_id):
        dfsex = pd.read_sql(select(Sex), engine)
        fig = px.pie(dfsex, values='rate', names='sex', color='sex', color_discrete_map={'남':'cyan', '여':'pink'}, title='본 성별 테이블')
    
    elif value =='성 비율' and ('btn-bongraph' in changed_id):
        dflastname = pd.read_sql(select(LastName), engine).head(30)
        fig = px.bar(dflastname, x='lastname', y='rate', title='본 성(姓) 테이블 상위 30개', color='rate', labels={'rate': '비율(%)', 'lastname':'성(姓)'})
        fig.update_yaxes(title_font=dict(size=20))
        
    
    elif value =='이름 비율' and ('btn-bongraph' in changed_id):
        dffirstname = pd.read_sql(select(FirstName), engine).head(15)
        labelss = dffirstname['firstname']
        valuess = dffirstname['rate']
        fig = go.Figure(data=[go.Pie(labels=labelss, values=valuess, hole=.3)],\
                     layout=go.Layout(title=go.layout.Title(text="이름")))
        fig.update_traces(title='본 이름 테이블 상위 15개')
    
    elif value =='나이 비율' and ('btn-bongraph' in changed_id):
        dfage = pd.read_sql(select(Age), engine)
        fig = px.scatter(dfage, x="age", y="rate", title='본 나이 테이블', color='rate', labels={'rate': '비율(%)', 'age': '나이(세)'})
        
    else:
        dfsex = pd.read_sql(select(Zero), engine)
        fig = px.bar(dfsex, x='rate', y='zero')
       
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)