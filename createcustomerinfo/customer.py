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


class Age(Base):
    __tablename__ = 'age'
    age = Column(String(30), primary_key=True)
    rate = Column(Float)


class Sex(Base):
    __tablename__ = 'sex'
    sex = Column(String(30), primary_key=True)
    rate = Column(Float)


class LastName(Base):
    __tablename__ = 'lastname'
    lastname = Column(String(30), primary_key=True)
    rate = Column(Float)


class FirstName(Base):
    __tablename__ = 'firstname'
    firstname = Column(String(30), primary_key=True)
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


metadata_obj.create_all(engine)


def DateOfBirth(age):
    #생년월일을 반환하는 함수
    #년수 찾기
    age_int = age[:age.find('세')]
    dt_now = datetime.datetime.now()
    years = int(dt_now.year) - int(age_int)

    #생년월일 생성
    str_datetime = f"{str(years)}-01-01"
    dt_datetime = datetime.datetime.strptime(str_datetime, '%Y-%m-%d').date()
    date = round(np.random.uniform(1, 365, 1)[0])
    return dt_datetime + datetime.timedelta(days=date)


def CreateCustomer(subscription, cnt):
    session = Session(engine)
    for i in range(cnt):
        #나이 비율에 맞게 뽑기
        agedata = pd.read_sql(select(Age), engine)
        age = agedata['age'].values.tolist()
        age_rate = agedata['rate'].values.tolist()
        age_in = random.choices(age, weights=age_rate)

        #생년월일
        dateofb = str(DateOfBirth(age_in[0]))

        #성별 비율에 맞게 뽑기
        sexdata = pd.read_sql(select(Sex), engine)
        sex = sexdata['sex'].values.tolist()
        sex_rate = sexdata['rate'].values.tolist()
        sex_in = random.choices(sex, weights=sex_rate)

        #성 비율에 맞게 뽑기
        lastnamedata = pd.read_sql(select(LastName), engine)
        lastname = lastnamedata['lastname'].values.tolist()
        last_rate = lastnamedata['rate'].values.tolist()
        lastname_in = random.choices(lastname, weights=last_rate)

        #이름 비율에 맞게 뽑기
        firstnamedata = pd.read_sql(select(FirstName), engine)
        firstname = firstnamedata['firstname'].values.tolist()
        first_rate = firstnamedata['rate'].values.tolist()
        firstname_in = random.choices(firstname, weights=first_rate)

        #테이블에 삽입
        for a, b, c in zip(lastname_in, firstname_in, sex_in):
            session.merge(Customer(lastname=a, firstname=b, sex=c, dateofbirth=dateofb, subdate=subscription))

    session.flush()
    session.commit()
    session.close()
    
    
def showsexrate():
    df = pd.read_sql(select(Customer), engine)
    dfsex = df.groupby(['sex'], as_index=False).count()
    dffig = dfsex.assign(rate = dfsex.cid.transform(func = lambda x : x / len(df.index)))
    fig = px.pie(dffig, values='rate', names='sex', color='sex', title='고객 테이블 성별')
    fig.show()
    
    dfsex = pd.read_sql(select(Sex), engine)
    figsex = px.pie(dfsex, values='rate', names='sex', color='sex', color_discrete_map={'남':'cyan', '여':'pink'}, title='본 성별 테이블')
    figsex.show()


def showfirstnamerate():
    df = pd.read_sql(select(Customer), engine)
    dffir = df.groupby(['firstname'], as_index=False).count()
    dffig = dffir.assign(rate = dffir.cid.transform(func = lambda x : x / len(df.index)))
    dffig = dffig.sort_values(by='rate' ,ascending=False).head(15)
    labelss = dffig['firstname']
    valuess = dffig['rate']
    fig = go.Figure(data=[go.Pie(labels=labelss, values=valuess, hole=.3)],\
                     layout=go.Layout(title=go.layout.Title(text="이름")))
    fig.update_traces(title='고객 테이블 이름 상위 15개')
    fig.show()
    
    dffirstname = pd.read_sql(select(FirstName), engine).head(15)
    labelss = dffirstname['firstname']
    valuess = dffirstname['rate']
    fig = go.Figure(data=[go.Pie(labels=labelss, values=valuess, hole=.3)],\
                     layout=go.Layout(title=go.layout.Title(text="이름")))
    fig.update_traces(title='본 이름 테이블 상위 15개')
    fig.show()

    
def showlastnamerate():
    df = pd.read_sql(select(Customer), engine)
    dflast = df.groupby(['lastname'], as_index=False).count()
    dffig = dflast.assign(rate = dflast.cid.transform(func = lambda x : x / len(df.index)))
    dffig = dffig.sort_values(by='rate' ,ascending=False).head(30)
    fig = px.bar(dffig, x="lastname", y="rate", title='고객 테이블 성(姓) 상위 30개 ', color='rate', labels={'rate': '비율(%)', 'lastname':'성(姓)'})
    fig.update_yaxes(title_font=dict(size=20))
    fig.show()
    
    dflastname = pd.read_sql(select(LastName), engine).head(30)
    figlastname = px.bar(dflastname, x='lastname', y='rate', title='본 성(姓) 테이블 상위 30개', color='rate', labels={'rate': '비율(%)', 'lastname':'성(姓)'})
    figlastname.update_yaxes(title_font=dict(size=20))
    figlastname.show()
    
def showdaterate():
    df = pd.read_sql(select(Customer), engine)
    df = df.assign(year = df['dateofbirth'].str[:4])
    dfdate = df.groupby(['year'], as_index=False).count()
    dffig = dfdate.assign(rate = dfdate.cid.transform(func = lambda x : x / len(df.index)))
    fig = px.scatter(dffig, x="year", y="rate", title='고객 테이블 생년월일', color='rate', labels={'rate': '비율(%)', 'age': '나이(세)'})
    fig.update_yaxes(title_font=dict(size=20))
    fig.show()
    
    dfage = pd.read_sql(select(Age), engine)
    fig = px.scatter(dfage, x="age", y="rate", title='본 나이 테이블', color='rate', labels={'rate': '비율(%)', 'age': '나이(세)'})
    fig.update_yaxes(title_font=dict(size=20))
    fig.show()

