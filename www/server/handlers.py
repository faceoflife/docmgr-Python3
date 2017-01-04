#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'url handlers, 处理各种URL请求'

import re, time, json, hashlib, base64, asyncio

from server.logger import logger

from server.web_framework import get, post

from server.models import User, Comment, Blog, next_id, EbookCatalog, EbookTags, EbookItem

from server.apis import Page, APIValueError, APIResourceNotFoundError, APIError, APIPermissionError

from server.conf.config import configs

from server import markdown2

from aiohttp import web

import pdb

# Admin's Email
_ADMIN_EMAIL = configs.admin.email
# Cookie Name
COOKIE_NAME = configs.cookie.name
# Cookie Secret's Key
_COOKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

# 转化页数为int型
def get_page_index(page_str):
	p  = 1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p

# 把存文本文件转为html格式的文本
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

# 检测当前用户是不是admin用户，不是抛异常
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

# 根据用户信息拼接一个cookie字符串
def user2cookie(user, max_age):
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time()) + max_age)
	# 过期时间是当前时间+设置的有效时间
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	# 构建cookie存储的信息字符串
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	# SHA1是一种单向算法，即可以通过原始字符串计算出SHA1结果，但无法通过SHA1结果反推出原始字符串。
	return '-'.join(L)

# 根据cookie字符串，解析出用户相关信息
async def cookie2user(cookie_str):
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			# 如果不是3个元素的话，与我们当初构造sha1字符串时不符，返回None
			return None
		uid, expires, sha1 = L
		# 分别获取到用户id，过期时间和sha1字符串
		if int(expires) < time.time():
			# 如果超时(超过一天)，返回None
			return None
		user = await User.find(uid)
		# 根据用户id(id为primary key)查找库，对比有没有该用户
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		# 根据查到的user的数据构造一个校验sha1字符串
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logger.info('invalid sha1')
			return None

		user.passwd = '*******'
		return user
	except Exception as e:
		logger.exception(e)
		return None

# -------------------------------------------------前后台首页入口-------------------------------------------------------------

# 前台首页入口
@get('/')
async def index(*, page='1'):
	return {
		'__template__': '/front/home.html'
	}

# 后台首页入口
@get('/admin')
async def admin():
    return {
        '__template__': '/console/home.html',
        'lbs': [
        	{'idx': '1', 'title': '00x600_1', 'src': '/static/image/placeholder_800x600_1.jpg'},
        	{'idx': '2', 'title': '00x600_2', 'src': '/static/image/placeholder_800x600_2.jpg'},
        	{'idx': '3', 'title': '00x600_3', 'src': '/static/image/placeholder_800x600_3.jpg'},
        	{'idx': '4', 'title': '00x600_4', 'src': '/static/image/placeholder_800x600_4.jpg'}
        ],
        'panels1': [
        	{'p_cls': 'uk-width-medium-1-3', 'title': 'Title1', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-3', 'title': 'Title2', 'icon': 'uk-icon-user', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-3', 'title': 'Title3', 'icon': 'uk-icon-bookmark', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'}
        ],
        'panels2': [
        	{'p_cls': 'uk-width-medium-1-5', 'title': 'Title1', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-5', 'title': 'Title2', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-5', 'title': 'Title3', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-5', 'title': 'Title4', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-5', 'title': 'Title5', 'icon': 'uk-icon-user', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'}
        ],
        'panels3': [
        	{'p_cls': 'uk-width-medium-1-2', 'title': 'Title1', 'icon': 'uk-icon-home', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'},
        	{'p_cls': 'uk-width-medium-1-2', 'title': 'Title2', 'icon': 'uk-icon-user', 'content': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor.'}
        ]
    }

# -----------------------------------------------------注册register、登录signin、注销signout-----------------------------------

# 注册页面
@get('/view/signup')
async def register():
    return {
        '__template__': '/console/signup.html'
    }

# 提交注册请求
@post('/api/signup')
async def api_signup(*, email, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
	# 判断email是否存在，且是否符合规定的正则表达式
		raise APIError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIError('passwd')

	users = await User.findAll('email=?', [email])
	# 查一下库里是否有相同的email地址，如果有的话提示用户email已经被注册过
	if len(users):
		raise APIError('register:failed', 'email', 'Email is already in use.')

	uid = next_id()
	# 生成一个当前要注册用户的唯一uid
	sha1_passwd = '%s:%s' % (uid, passwd)

	admin = False
	if email == _ADMIN_EMAIL:
		admin = True

	# 创建一个用户（密码是通过sha1加密保存）
	user = User(id = uid, name = name.strip(), email = email, passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
		image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest(), admin=admin)
	# 注意数据库中存储的passwd是经过SHA1计算后的40位Hash字符串，所以服务器端并不知道用户的原始口令。

	# 保存这个用户到数据库用户表
	await user.save()
	logger.info('save user OK')

	# 构建返回信息
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly = True)
	user.passwd = '******'
	# 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii = False, default = lambda o:o.__dict__).encode('utf-8')
	return r

# 登陆页面
@get('/view/signin')
async def signin():
    return {
        '__template__': '/console/signin.html',
        'admin_email': _ADMIN_EMAIL
    }

# 登陆请求
@post('/api/signin')
async def authenticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')

	users = await User.findAll('email=?', [email])
	# 根据email在库里查找匹配的用户
	if not len(users):
		raise APIValueError('email', 'email not exist')
	user = users[0]

	browser_sha1_passwd = '%s:%s' % (user.id, passwd)
	browser_sha1 = hashlib.sha1(browser_sha1_passwd.encode('utf-8'))
	'''
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	# 在Python 3.x版本中，把'xxx'和u'xxx'统一成Unicode编码，即写不写前缀u都是一样的，而以字节形式表示的字符串则必须加上b前缀：b'xxx'。
	sha1.update(passwd.encode('utf-8'))
	'''
	if user.passwd != browser_sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid passwd')
	
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly = True)
	user.passwd = '*********'
	# 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii = False, default = lambda o:o.__dict__).encode('utf-8')
	return r    

# 登出操作
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    # 清理掉cookie得用户信息数据
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logger.info('user signed out')
    return r

# -----------------------------------------------------用户管理------------------------------------

@get('/manage/users')
async def manage_users(*, page='1'):
    # 查看所有用户
    return {
        '__template__': '/console/manage_users.html',
        'page_index': get_page_index(page),
        '__breadcrumb__': 'users'
    }

@get('/api/users')
async def api_get_users(*, page='1'):
    # 返回所有的用户信息jason格式
    page_index = get_page_index(page)
    total = await User.findNumber('count(id)')
    if not total or total == 0:
    	return dict(page=page, users=[])

    p = Page(total, page_index)
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    logger.info('users = %s and type = %s' % (users, type(users)))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

# ------------------------------------------博客管理的URL处理函数----------------------------------

# 进入博客列表页面
@get('/view/blogs')
async def blogs(*, page='1'):
	# 获取到要展示的博客页数是第几页
	page_index = get_page_index(page)
	# 查找博客表里的条目数
	num = await Blog.findNumber('count(id)')

	# 如果表里没有条目，则不需要显示
	if (not num) and num == 0:
		logger.info('the type of num is: %s' % type(num))
		blogs = []
	else:
		# 通过Page类来计算当前页的相关信息
		page = Page(num, page_index)

		# 否则，根据计算出来的offset(取的初始条目index)和limit(取的条数)，来取出条目
		blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
	# 返回给浏览器
	return {
		'__template__': '/front/blogs.html',
		'page': page,
		'blogs': blogs
	}

# 进入博客管理页面
@get('/manage/blogs')
async def manage_blogs(*, page = '1'):
	# 博客管理页面
	return {
		'__template__': "/console/manage_blogs.html",
		'page_index': get_page_index(page),
		'__breadcrumb__': 'blogs'
	}

# 进入创建博客页面
@get('/manage/blogs/create')
async def manage_create_blog():
	# 写博客页面
	return {
		'__template__': '/console/manage_blog_edit.html',
		'__breadcrumb__': 'blogs',
		'id': '',
		'action': '/api/blogs' # 对应HTML页面中VUE的action名字
	}

# 提交创建博客请求
@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
	check_admin(request)
	# 只有管理员可以写博客, 调用位置：manage_blog_edit.html 22行
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')		
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')				

	blog = Blog(user_id = request.__user__.id, user_name = request.__user__.name, user_image = request.__user__.image, name = name.strip(), summary = summary.strip(), content = content.strip())
	await blog.save()
	return blog

# 分页获取博客列表
@get('/api/blogs')
async def api_blogs(*, page = '1'):
	''' 获取博客信息,调用位置：manage_blogs.html 40行
		请参考29行的api_get_users函数的注释 '''
	page_index = get_page_index(page)
	blog_count = await Blog.findNumber('count(id)')
	p = Page(blog_count, page_index)
	logger.info('p: %s', p)
	if blog_count == 0:
		return dict(page = p, blogs = ())
	blogs = await Blog.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
	return dict(page = p, blogs = blogs)

# 获取指定ID的博客及评论内容
@get('/view/blog/{id}')
async def get_blog(id):
	 # 根据博客id查询该博客信息
	 blog = await Blog.find(id)
	 # 根据博客id查询该条博客的评论
	 comments = await Comment.findAll('blog_id=?', [id], orderBy = 'created_at desc')
	 # markdown2是个扩展模块，这里把博客正文和评论套入到markdonw2中
	 for c in comments:
	 	c.html_content = text2html(c.content)

	 blog.html_content = markdown2.markdown(blog.content)

	 return {
	 	'__template__': '/front/blog.html',
	 	'blog': blog,
	 	'comments': comments
	 }

# 获取某条博客的信息
@get('/api/blogs/{id}')
async def api_get_blog(*, id):
	blog = await Blog.find(id)
	return blog

# 删除一条博客
@post('/api/blogs/{id}/delete')
async def api_delete_blog(id, request):
    logger.info("删除博客的博客ID为：%s" % id)
    # 先检查是否是管理员操作，只有管理员才有删除评论权限
    check_admin(request)
    # 查询一下博客id是否有对应的博客
    b = await Blog.find(id)
    # 没有的话抛出错误
    if b is None:
        raise APIResourceNotFoundError('Blog')
    # 有的话删除
    await b.remove()
    return dict(id=id)

# 进入修改博客的页面
@get('/manage/blogs/{id}/modify')
async def manage_modify_blog(id):
    return {
        '__template__': '/console/manage_blog_modify.html',
        '__breadcrumb__': 'blogs',
        'id': id,
        'action': '/api/blogs/modify'
    }  

# 修改一条博客
@post('/api/blogs/modify')
async def api_modify_blog(request, *, id, name, summary, content):
    logger.info("修改的博客的博客ID为：%s", id)
    # name，summary,content 不能为空
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')

    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')

    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    # 获取指定id的blog数据
    blog = await Blog.find(id)
    blog.name = name
    blog.summary = summary
    blog.content = content

    # 保存
    await blog.update()
    return blog    	

# ----------------------------------------------------评论管理-----------------------------------------------------

# 评论管理页面
@get('/manage/comments')
async def manage_comments(*, page='1'):
    return {
        '__template__': '/console/manage_comments.html',
        'page_index': get_page_index(page),
        '__breadcrumb__': 'comments'
    }

# 根据page获取评论，注释可参考 index 函数的注释，不细写了
@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)

# 对某个博客发表评论
@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    user = request.__user__
    # 必须为登陆状态下，评论
    if user is None:
        raise APIPermissionError('content')
    # 评论不能为空
    if not content or not content.strip():
        raise APIValueError('content')
    # 查询一下博客id是否有对应的博客
    blog = await Blog.find(id)
    # 没有的话抛出错误
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    # 构建一条评论数据
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name,
                      user_image=user.image, content=content.strip())
    # 保存到评论表里
    await comment.save()
    return comment

# 删除某个评论
@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
    logger.info('要删除的评论ID：%s', id)
    # 先检查是否是管理员操作，只有管理员才有删除评论权限
    check_admin(request)
    # 查询一下评论id是否有对应的评论
    c = await Comment.find(id)
    # 没有的话抛出错误
    if c is None:
        raise APIResourceNotFoundError('Comment')
    # 有的话删除
    await c.remove()
    return dict(id=id)   

# --------------------------------------------电子书管理----------------------------------------

@get('/view/ebooks')
async def ebooks_view(*, page='1'):
	'''分页获取电子书列表'''
	page_index = get_page_index(page)
	total = await EbookCatalog.findNumber('count(id)', 'p_id = ?', ['-1'])

	if not total or total == 0:
		catalogs = []
	else:
		# 通过Page类来计算当前页的相关信息
		page = Page(total, page_index)
		catalogs = await EbookCatalog.findAll('p_id = ?', ['-1'], orderBy='created_at desc', limit=(page.offset, page.limit))

	return {
        '__template__': '/front/ebooks.html',
        'page': page,
        'catalogs': catalogs
    }

@get('/view/ebooks/{catalog_id}/{item_id}')
async def ebook_view(catalog_id, item_id, request):
	catalog = await EbookCatalog.find(catalog_id)
	if catalog is None:
		raise APIResourceNotFoundError('EbookCatalog[%s] Not Found.', catalog_id)
	# ''' 若item_id等于catalog的创建时间，说明为是获得目录的页面请求 '''
	logger.info('item_id: %s, created_at: %s', item_id, catalog.created_at)
	if item_id == catalog.id:
		p_items = await EbookItem.findAll('catalog_id = ? and p_id = ?', [catalog_id, '-1'], orderBy='order_seq asc')
		for p in p_items:
			p.content = None # ''' 将内容置为None，节省带宽 '''
			ebook_items = await EbookItem.findAll('catalog_id = ? and p_id = ?', [catalog_id, p.id], orderBy='order_seq asc')
			for ebook_item in ebook_items:
				ebook_item.content = None # ''' 将内容置为None，节省带宽 '''
			p.index_items = ebook_items
		catalog.p_items = p_items

		return {
			'__template__': '/front/ebook_index.html',
			'__breadcrumb__': 'ebooks',
			'ebook': catalog
		}
	else:
		ebook = await EbookItem.find(item_id)
		if ebook is None:
			raise APIResourceNotFoundError('EbookItem[%s] Not Found.', item_id)
		ebook.cover_img = catalog.cover_img
		ebook.author = catalog.author

		return {
			'__template__': '/front/ebook.html',
			'__breadcrumb__': 'ebooks',
			'ebook': ebook
		}


@get('/manage/ebooks')
async def manage_ebooks(*, page='1'):
	return {
        '__template__': '/console/manage_ebooks.html',
        'page_index': get_page_index(page),
        '__breadcrumb__': 'ebooks'
    }

@get('/api/ebooks')
async def api_get_ebooks(*, page='1'):
	page_index = get_page_index(page)
	total = await EbookCatalog.findNumber('count(id)')
	
	if not total or total == 0:
		return dict(page=page, catalogs=[])

	p = Page(total, page_index)
	catalogs = await EbookCatalog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, catalogs=catalogs)

@post('/api/ebooks')
async def api_post_ebooks(request, *, id, name, summary, content):
	check_admin(request)
	# 只有管理员可以写博客, 调用位置：manage_blog_edit.html 22行
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')		
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')				

	blog = Blog(user_id = request.__user__.id, user_name = request.__user__.name, user_image = request.__user__.image, name = name.strip(), summary = summary.strip(), content = content.strip())
	await blog.save()
	return blog


@get('/manage/ebooks/create')
async def ebooks_create():
	tags = await EbookTags.findAll(orderBy='order_seq desc, created_at desc');
	catalogs = await EbookCatalog.findAll('p_id = ?', ['-1'], orderBy='created_at desc')
	return {
		'__template__': '/console/manage_ebook_edit.html',
		'__breadcrumb__': 'ebooks',
		'tags': tags,
		'catalogs': catalogs,
		'id': '',
		'action': '/api/ebooks' # 对应HTML页面中VUE的action名字
	}


@get('/manage/ebooks/{id}/modify')
async def ebooks_modify(id, *, request):
	tags = await EbookTags.findAll(orderBy='order_seq desc, created_at desc');
	return {
		'__template__': '/console/manage_ebook_edit.html',
		'__breadcrumb__': 'ebooks',
		'tags': tags,
		'id': '',
		'action': '/api/ebooks' # 对应HTML页面中VUE的action名字
	}

'''
[
	{'id': '1', 'name': 'python', 'badge_type': 'uk-badge-success'},
	{'id': '2', 'name': 'Java', 'badge_type': 'uk-badge-success'},
	{'id': '3', 'name': 'NodeJs', 'badge_type': 'uk-badge-warning'},
	{'id': '4', 'name': 'Vue', 'badge_type': 'uk-badge-success'},
]
'''

@get('/manage/tags')
async def manage_tags():
	tags = await EbookTags.findAll(orderBy='order_seq desc');
	return {
		'__template__': '/console/manage_tags.html',
		'__breadcrumb__': 'tags',
		'tags': tags
	}




