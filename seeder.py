from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Catalog, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user = User(name="omar", email="omaralem82@gmail.com")
session.add(user)
session.commit()

catalog = Catalog(name="pop")
session.add(catalog)
session.commit()

item = Item(user_id=1, name="lily", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="a", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="b", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="c", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="d", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="e", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="f", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="g", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()


catalog = Catalog(name="rock")
session.add(catalog)
session.commit()

item = Item(user_id=1, name="lily-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="a-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="b-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="c-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="d-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="e-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="f-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()

item = Item(user_id=1, name="g-rock", catalog=catalog)
item.description = "written by bla bla bla bla"
session.add(item)
session.commit()
