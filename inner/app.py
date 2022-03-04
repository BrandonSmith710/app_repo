from .data import df, clean_text
from flask import Flask, render_template, request, Response
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import pickle
from sklearn.ensemble import RandomForestClassifier
import cv2

DB = SQLAlchemy()
class Song(DB.Model):
            # enter string as first arg to set colname diff than varname
            # also can use multiple primary_keys for compound primary_key
    id = DB.Column(DB.String(50), primary_key=True, nullable=False)
    name = DB.Column(DB.String(50), nullable=False)
    acoustic = DB.Column(DB.Float, nullable=False)
    danceable = DB.Column(DB.Float, nullable=False)
    energy = DB.Column(DB.Float, nullable=False)
    loudness = DB.Column(DB.Float, nullable=False)
    mode = DB.Column(DB.Float, nullable=False)
    liveness = DB.Column(DB.Float, nullable=False)
    valence = DB.Column(DB.Float, nullable=False)
    tempo = DB.Column(DB.Float, nullable=False)
    duration_ms = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'{self.name} is {round(self.duration_ms*60000, 2)} minutes long'

camera = cv2.VideoCapture(0)
def generate_frames():
    # success ; bool ; True == can read camera

    while True:

        success, frame= camera.read()
        if not success:
            break
        else:             # imencode encodes img to memory buffer
            ret, buffer=cv2.imencode('.jpg', frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
'''
suggest a song to the user based on the querying song(i.e. a song the user
just listened to, or a song the user has indicated they enjoy).
'''
# app factory
def create_app():
    # instantiate app
    APP = Flask(__name__)

    model = pickle.load(open('rf_model2.h5', 'rb'))


    # configure database
    APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_spotify.sqlite3'
    APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # initializing app
    DB.init_app(APP)
    # create tables
    @APP.before_first_request
    def create_tables():
        DB.create_all()
    @APP.route('/', methods=['GET', 'POST'])
    def root():
        if request.method == 'POST':
            # Get form data
            id = request.form.get('search')

            # id = id.split()
            # print(id))
            # res = [x for x in Song.query.all() if x.id == num]
            res = Song.query.get(id)

            if res:

            # print(num in ' '.join(b.id for b in res))            
                return render_template('results.html', answer=res.__repr__())

            # in case the user entry is invalid
            # except:
            #     return render_template('base.html', content='seeyos', title='Failure69')
            
        return render_template('base.html', title='Home')

    @APP.route('/classify', methods=['GET', 'POST'])
    def classify():
        # res=''
        if request.method == 'POST':
            # Get form data
            text = request.form.get('search')

            print(text)
            clean = clean_text(text)

            # model = pickle.load(open('class_model.h5', 'rb'))

            res = model.predict([clean])
            res = res[0]
            res = 'Related to natural disaster' if res > 0 else 'Unrelated to natural disaster'

            # print(num in ' '.join(b.id for b in res))            
            return render_template('classify.html', answer=res)

            
        
            # in case the user entry is invalid
            # except:
            #     return render_template('base.html', content='seeyos', title='Failure69')
            
        return render_template('base2.html', content='seeyos', title='Home')

    # route for wiping the database clean/creating tables
    

    @APP.route('/refresh')
    def refresh():
        DB.drop_all()
        DB.create_all()
        return 'Data has been refreshed.'

    @APP.route('/add')
    def add_one():
        '''Adds 1000 rows of data for 1000 songs'''

        """'id', 'name', 'acousticness', 'danceability', 'energy', 'loudness',
                 'mode', 'liveness', 'valence', 'tempo', 'duration_ms'"""
        for x in range(1000):
            i, n, a, d, e, l, m, li, v, t, d = df.iloc[x].values
            temp = Song(id=i, name=n, acoustic=a, danceable=d, energy=e, loudness=l, mode=m, liveness=li,
                        valence=v, tempo=t, duration_ms=d)

                        # query.get only used for primary keys
            if not Song.query.get(temp.id):
                DB.session.add(temp)

        # commit changes to database session
        DB.session.commit()
        # return Song.query.filter(Song.danceable >= .2).first().__repr__()
        return 'Songs have bean added'


    @APP.route('/query')
    def query():

        # res = df1.iloc[[x for x in range(len(df)) if df1.iloc[x]['danceability'] >= .2]]
        return Song.query.filter(Song.danceable >= .2).first().__repr__()

        # return ' '.join(map(str, df1.iloc[42069].values))



    @APP.route('/watchthis')
    def watchthis():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    return APP





    
