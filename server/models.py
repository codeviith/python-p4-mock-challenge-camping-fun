from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities_table'

    serialize_rules = ("-signups.activity",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship("Signup", back_populates="activity", cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups_table'

    serialize_rules = ("-activity.signups","-camper.signups")

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities_table.id"))
    camper_id = db.Column(db.Integer, db.ForeignKey("campers_table.id"))

    activity = db.relationship("Activity", back_populates="signups")
    camper = db.relationship("Camper", back_populates="signups")


    @validates('time')
    def validate_time(self, key, time):
        if 0 <= time <= 23:
            return time
        else:
            raise ValueError ("Time to complete signup must be within 23 minutes.")
    

    def __repr__(self):
        return f'<Signup {self.id}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers_table'

    serialize_rules = ("-signups.camper",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False) ### nullable = false is validating that the name cannot be empty.
    age = db.Column(db.Integer)

    signups = db.relationship("Signup", back_populates="camper")


    @validates('age')
    def validate_age(self, key, age):
        if 8 <= age <= 18:
            return age
        else:
            raise ValueError ("Signup age must be between 8 and 18.")


    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


