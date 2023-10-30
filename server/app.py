#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def get_post_all_camper():
    if request.method == 'GET':
        campers = Camper.query.all()
        
        ### option 1: for loop
        # body = []
        # for camper in campers:
        #     body.append(camper.to_dict())

        ### option 2: list comprehension
        return ([camper.to_dict(rules=("-signups",)) for camper in campers], 200)
    elif request.method == 'POST':
        data = request.get_json()

        try:
            new_camper = Camper(
                name=data.get('name'),
                age=data.get('age')
            )
        except Exception:
            return ({"error": "Cannot create new camper."}, 405)
        
        db.session.add(new_camper)
        db.session.commit()

        return make_response(new_camper.to_dict(rules=("-signups",)), 201)


@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def get_patch_camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        return {"error": "Camper not found."}, 404
    
    if request.method == 'GET':
        return make_response(camper.to_dict(), 200)
    elif request.method == 'PATCH':
        data = request.get_json()

        for key in data:
            try:
                setattr(camper, key, data[key])
            except ValueError as e: ### "as e" is to set the ValueError into the 'e' variable.
                return {"errors": [str(e)]}, 400 ### str(e) is what converts the e variable to
                                                 ### a string so we can see what the error is.
                                                    ### but why is in in brackets???
        db.session.add(camper)
        db.session.commit()

        return make_response(camper.to_dict(rules=("-signups",)), 200)

@app.get('/activities')
def get_all_activities():
    activities = Activity.query.all()
    return make_response([activity.to_dict(rules=("-signups",)) for activity in activities], 200)

@app.delete('/activities/<int:id>')
def activity_by_id(id):
    activity = Activity.query.filter( Activity.id == id).first()

    if not activity:
        return {"error": "Activity not found."}, 404
    
    db.session.delete(activity)
    db.session.commit()

    return {"message": "Activity deleted."}, 200

@app.post('/signups')
def post_all_signups():
    data = request.get_json()

    try:
        new_signup = Signup(
            time = data.get('time'),
            camper_id = data.get('camper_id'),
            activity_id = data.get('activity_id')
        )
    except ValueError:
        return {"errors": "Cannot create new signup."}, 405
    
    db.session.add(new_signup)
    db.session.commit()

    return make_response(new_signup.to_dict(), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
