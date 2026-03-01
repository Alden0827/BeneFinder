from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'tbl_users'
    __table_args__ = {'schema': 'public'}

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255))
    firstname = db.Column(db.String(100))
    middlename = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    group_id = db.Column(db.Integer)
    status = db.Column(db.String(20))

    def get_id(self):
        return str(self.user_id)

class Roster(db.Model):
    __tablename__ = 'tbl_roster'
    __table_args__ = {'schema': 'ds'}

    entry_id = db.Column(db.BigInteger, primary_key=True)
    hh_id = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birthday = db.Column(db.Date)
    sex = db.Column(db.String(10))
    province = db.Column(db.String(100))
    municipality = db.Column(db.String(100))
    barangay = db.Column(db.String(100))
    client_status = db.Column(db.String(50))
    hh_set = db.Column(db.String(50))
    prog = db.Column(db.String(50))
    relation_to_hh_head = db.Column(db.String(100))
    grantee = db.Column(db.String(10))
    member_status = db.Column(db.String(50))
