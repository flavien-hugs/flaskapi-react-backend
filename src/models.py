from . import db

from datetime import datetime


"""
class Recipe:
    id: int primary key
    rcp_title: str
    rcp_desc: str (text)
    rcp_created: date
    rcp_updated: date
"""


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class Recipe(Updateable, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    rcp_title = db.Column(db.String(80), nullable=False)
    rcp_desc = db.Column(db.Text(), nullable=False)
    rcp_created = db.Column(db.DateTime, default=datetime.utcnow())
    rcp_updated = db.Column(db.DateTime, onupdate=datetime.utcnow())

    def __repr__(self):
        return f"<Recipe self.rcp_title>"

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
