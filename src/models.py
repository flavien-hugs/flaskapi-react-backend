from sqlalchemy import orm

from . import db

from datetime import datetime


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class ModelAbstract(object):
    rcp_created = db.Column(db.DateTime, default=datetime.utcnow())
    rcp_updated = db.Column(db.DateTime, onupdate=datetime.utcnow())


"""
class User:
    id: int primary key
    user_fullname: str
    user_addr_email: str
    user_password: str
    rcp_created: date
    rcp_updated: date
"""


class User(Updateable, db.Model, ModelAbstract):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_fullname = db.Column(db.String(100), nullable=False)
    user_addr_email = db.Column(db.String(80), unique=True, nullable=False)
    user_password = db.Column(db.Text(), nullable=False)
    recipes = db.relationship("Recipe", backref="user", lazy="dynamic")

    def recipes_select(self):
        return Recipe.select().where(orm.with_parent(self, User.recipes))

    def __repr__(self):
        return f"<User {self.user_fullname}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, user_fullname, user_addr_email):
        self.user_fullname = user_fullname
        self.user_addr_email = user_addr_email
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



"""
class Recipe:
    id: int primary key
    rcp_title: str
    rcp_desc: str (text)
    rcp_created: date
    rcp_updated: date
"""


class Recipe(Updateable, db.Model, ModelAbstract):

    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True, index=True)
    rcp_title = db.Column(db.String(80), nullable=False)
    rcp_desc = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)
    author = orm.relationship('User', back_populates='recipes')

    def __repr__(self):
        return f"<Recipe {self.rcp_title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, rcp_title, rcp_desc):
        self.rcp_title = rcp_title
        self.rcp_desc = rcp_desc
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
