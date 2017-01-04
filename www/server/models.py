#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time, uuid

from server.orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)
    
    def __init__(self, **kw):
        super(User, self).__init__(**kw)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(Blog, self).__init__(**kw)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(Comment, self).__init__(**kw)

class Catagory(Model):
    __table__ = 'catagory'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    enum = StringField(ddl='varchar(2)')
    name = StringField(ddl='varchar(100)')
    icon = StringField(ddl='varchar(50)')
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(Catagory, self).__init__(**kw)

class EbookCatalog(Model):
    __table__ = 'ebook_catalog'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    tags = StringField(ddl='varchar(500)')
    title = StringField(ddl='varchar(50)')
    author = StringField(ddl='varchar(200)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    cover_img = StringField(ddl='varchar(200)')
    source_link = StringField(ddl='varchar(200)')
    order_seq = IntegerField(default=1)
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(EbookCatalog, self).__init__(**kw)

class EbookItem(Model):
    __table__ = 'ebook_item'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    catalog_id = StringField(ddl='varchar(50)')
    p_id = StringField(ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    content = TextField()
    order_seq = IntegerField(default=99)
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(EbookItem, self).__init__(**kw)

class EbookTags(Model):
    __table__ = 'ebook_tags'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    badge_type = StringField(ddl='varchar(50)')
    order_seq = IntegerField(default=1)
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(EbookTags, self).__init__(**kw)


