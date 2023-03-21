# encoding:utf-8

from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import redis
import qrcode
from io import BytesIO
# import PyRSS2Gen
import random
import re
import base64
import json
import codecs
import time
import os
import datetime
from flask import Flask, request, render_template, session, g, url_for, redirect, flash, current_app, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, cast, func
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babelex import Babel
from getpass import getpass
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
import jieba
import jieba.analyse
import MySQLdb
import MySQLdb.cursors

# Initialize Flask and set some config values
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'gSfhsauyvgeyt23478396#@$#^#$G652659'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:db@8837609@127.0.0.1:3306/dhtdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 5000
db = SQLAlchemy(app)
manager = Manager(app)
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': '',
    'CACHE_REDIS_PASSWORD': ''
})
cache.init_app(app)

DB_HOST = '127.0.0.1'
DB_NAME_MYSQL = 'dhtdb'
DB_PORT_MYSQL = 3306
DB_NAME_SPHINX = 'film'
DB_PORT_SPHINX = 9306
DB_USER = 'root'
DB_PASS = 'db@8837609'
DB_CHARSET = 'utf8mb4'

sitename = "Btdad"
domain = "https://www.btdad.com/"
yesterday = int(time.mktime(datetime.datetime.now().timetuple())) - 86400
thisweek = int(time.mktime(datetime.datetime.now().timetuple())) - 86400 * 7

class LoginForm(FlaskForm):
    name = StringField('用户名: ', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField('密码: ', validators=[DataRequired(), Length(1, 20)])

    def get_user(self):
        return db.session.query(User).filter_by(name=self.name.data).first()

class ComplaintForm(FlaskForm):
    info_hash = StringField('Hash: ', validators=[DataRequired()])
    reason = TextAreaField('原因: ', validators=[DataRequired()])
    submit = SubmitField('屏蔽')

class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')

class Complaint(db.Model):
    """ DMCA投诉记录 """
    __tablename__ = 'complaint'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    info_hash = db.Column(db.String(40), unique=True, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

class Search_Filelist(db.Model):
    """ 文件列表 """
    __tablename__ = 'search_filelist'
    info_hash = db.Column(db.String(40), primary_key=True, nullable=False)
    file_list = db.Column(db.Text, nullable=False)

class Search_Hash(db.Model, UserMixin):
    __tablename__ = 'search_hash'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    info_hash = db.Column(db.String(40), unique=True)
    category = db.Column(db.String(20))
    data_hash = db.Column(db.String(32))
    name = db.Column(db.String(200))
    extension = db.Column(db.String(20))
    classified = db.Column(db.Boolean())
    source_ip = db.Column(db.String(20))
    tagged = db.Column(db.Boolean(), default=False)
    length = db.Column(db.BigInteger)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.now)
    requests = db.Column(db.Integer)
    comment = db.Column(db.String(100))
    creator = db.Column(db.String(20))

class Search_Keywords(db.Model):
    """ 番号列表 """
    __tablename__ = 'search_keywords'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    keyword = db.Column(db.String(20), nullable=False, unique=True)
    order = db.Column(db.Integer, nullable=False)
    pic = db.Column(db.String(100), nullable=False)
    score = db.Column(db.String(10), nullable=False)

class Search_Tags(db.Model):
    """ 搜索记录 """
    __tablename__ = 'search_tags'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    tag = db.Column(db.String(50), nullable=False, unique=True)

class Search_Statusreport(db.Model):
    """ 爬取统计 """
    __tablename__ = 'search_statusreport'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.datetime.now)
    new_hashes = db.Column(db.Integer, nullable=False)
    total_requests = db.Column(db.Integer, nullable=False)
    valid_requests = db.Column(db.Integer, nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.username


def make_shell_context():
    return dict(app=app, db=db, Complaint=Complaint, Search_Filelist=Search_Filelist, Search_Hash=Search_Hash, Search_Tags=Search_Tags)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')

def replace_keyword_filter(str, old, new):
    return re.sub(r'(?i)('+old+')', new, str)
app.add_template_filter(replace_keyword_filter,'replace')

def todate_filter(s):
    return datetime.datetime.fromtimestamp(int(s)).strftime('%Y-%m-%d')
app.add_template_filter(todate_filter, 'todate')

def fromjson_filter(s):
    try:
        return json.loads(s)
    except ValueError:
        pass
app.add_template_filter(fromjson_filter, 'fromjson')

def tothunder_filter(magnet):
    return base64.b64encode('AA' + magnet + 'ZZ')
app.add_template_filter(tothunder_filter, 'tothunder')

categoryquery = {0: "", 1: "and category='影视'", 2: "and category='音乐'", 3: "and category='图像'",
                 4: "and category='文档书籍'", 5: "and category='压缩文件'", 6: "and category='安装包'", 7: "and category='其他'"}

sorts = {0: "", 1: "ORDER BY length DESC", 2: "ORDER BY create_time DESC", 3: "ORDER BY requests DESC", 4: "ORDER BY last_seen DESC"}


def geticon_filter(ext):
    cats = {"html": ".html", "nfo": ".nfo", "pdf": ".pdf", "url": ".url",  "inf": ".inf", "chm": ".chm", "flash": ".swf", "mp4": ".mp4", "exe": ".exe", "iso": ".iso", 
    "txt": [".txt", ".text"], "video": [".avi", ".rmvb", ".m2ts", ".wmv", ".mkv", ".flv", ".qmv", ".rm", ".mov", ".vob", ".asf", ".3gp", ".mpg", ".mpeg", ".m4v", ".f4v", ".ts"], 
    "jpg": [".jpg", ".jpeg", ".bmp", ".png", ".gif", ".tiff"], "mp3": [".mp3", ".wma", ".wav", ".dts", ".mdf", ".mid", ".midi"], "audio": [".aac", ".flac", ".ape"], 
    "rar": [".zip", ".rar", ".7z", ".tar", ".gz", ".dmg", ".pkg"]}
    for k, v in cats.iteritems():
        if ext in v:
            return k
    return "other"
app.add_template_filter(geticon_filter, 'geticon')

def fenci_filter(title, n):
    return jieba.analyse.extract_tags(title, n)
app.add_template_filter(fenci_filter, 'fenci')

def filelist_filter(info_hash):
    try:
        return json.loads(Search_Filelist.query.filter_by(info_hash=info_hash).first().file_list)
    except:
        return [{
            'path': Search_Hash.query.filter_by(info_hash=info_hash).first().name,
            'length': Search_Hash.query.filter_by(info_hash=info_hash).first().length
        }]
app.add_template_filter(filelist_filter, 'filelist')

def sphinx_conn():
    conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT_SPHINX, user=DB_USER, passwd=DB_PASS, db=DB_NAME_SPHINX,
                           charset=DB_CHARSET, cursorclass=MySQLdb.cursors.DictCursor, use_unicode=False)
    curr = conn.cursor()
    return (conn,curr)
    
def sphinx_close(curr,conn):
    curr.close()
    conn.close()

def gethash_filter(id):
    conn,curr = sphinx_conn()
    hashsql = 'SELECT * FROM film WHERE id=%s'
    curr.execute(hashsql,[id])
    hash = curr.fetchone()
    sphinx_close(curr,conn)
    return hash
app.add_template_filter(gethash_filter, 'gethash')

def searchagain_filter(query, id):
    conn,curr = sphinx_conn()
    hashsql = 'SELECT * FROM film WHERE match(%s) and id<>%s limit 10'
    curr.execute(hashsql, [query, id])
    hashlist = curr.fetchall()
    sphinx_close(curr,conn)
    return hashlist
app.add_template_filter(searchagain_filter, 'searchagain')

def getvote_filter(info_hash, votenum):
    if not r.exists("vote_{}_{}".format(votenum, info_hash)):
        r.set("vote_{}_{}".format(votenum, info_hash), 0)
    votenumber = r.get("vote_{}_{}".format(votenum, info_hash))
    return votenumber
app.add_template_filter(getvote_filter, 'getvote')

def detailextension_filter(name):
    return name.split('.')[-1]
app.add_template_filter(detailextension_filter, 'detailextension')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=60)

r = redis.Redis(host='localhost', port=6379, db=0)
r.set("totals", 9565871)

@app.route('/', methods=['GET', 'POST'])
def index():
    r.incrby("totals", 8)
    total = r.get("totals")
    tags = Search_Tags.query.order_by(Search_Tags.id.desc()).limit(30)
    form = SearchForm()
    return render_template('index.html', form=form, total=total, tags=tags, sitename=sitename)

@app.route('/search-<query>-<int:category>-<int:order>-<int:page>.html', methods=['GET', 'POST'])
@cache.cached(timeout=60*1,key_prefix=make_cache_key)
def search_results(query, category, order, page=1):
    form = SearchForm()
    if re.match(r"^['`=\(\)\|\!\-\@\~\"\&\/\\\^\$].*?", query) or re.match(r".*?['`=\(\)\|\!\-\@\~\"\&\/\\\^\$]$", query):
        return render_template('404.html', form=form, sitename=sitename)
    query = re.sub(r"['`=\(\)\|\!\@\~\"\&\/\\\^\$]", r"", query)
    query = re.sub(r"(-+)", r"-", query)
    query = ' '.join(query.encode('utf-8').lower().split())
    sensitivewordslist = sensitivewords()
    for word in sensitivewordslist:
        if word.search(query):
            return render_template('wordnotallowed.html', form=form, sitename=sitename)
    connzsky = MySQLdb.connect(host=DB_HOST, port=DB_PORT_MYSQL, user=DB_USER, passwd=DB_PASS, db=DB_NAME_MYSQL,
                                charset=DB_CHARSET, cursorclass=MySQLdb.cursors.DictCursor, use_unicode=False)
    currzsky = connzsky.cursor()
    taginsertsql = 'REPLACE INTO search_tags(tag) VALUES(%s)'
    currzsky.execute(taginsertsql, [query])
    connzsky.commit()
    currzsky.close()
    connzsky.close()
    conn,curr = sphinx_conn()
    sqlpre = ' SELECT * FROM film WHERE match(%s)'
    sqlend = ' limit %s,20 OPTION max_matches=50000 '
    searchsql = sqlpre + categoryquery[category] + sorts[order] + sqlend
    curr.execute(searchsql, [query, (page - 1) * 20])
    searchresult = curr.fetchall()
    countssql = 'SHOW META'
    curr.execute(countssql)
    countsresult = curr.fetchall()
    counts = int(countsresult[0]['Value'])
    taketime = float(countsresult[2]['Value'])
    tags = Search_Tags.query.order_by(Search_Tags.id.desc()).limit(30)
    categorycountslist = []
    for x in categoryquery.values():
        categorycountssql = 'SELECT count(*) FROM film WHERE match(%s) ' + x
        curr.execute(categorycountssql, [query])
        categorycounts = curr.fetchall()
        categorycountslist.append(categorycounts[0]['count(*)'])
    sphinx_close(curr,conn)
    pages = (counts + 19) / 20
    form.search.data = query
    return render_template('list.html', form=form, query=query, pages=pages, page=page, category=category, order=order,
                        hashs=searchresult, counts=counts, categorycountslist=categorycountslist, taketime=taketime,
                        tags=tags, sitename=sitename)

def sensitivewords():
    sensitivewordslist = []
    sensitivefile = os.path.join(
        os.path.dirname(__file__), 'sensitivewords.txt')
    with open(sensitivefile, 'rb') as f:
        for line in f:
            word = re.compile(line.rstrip('\r\n\t'))
            sensitivewordslist.append(word)
    return sensitivewordslist

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if not form.search.data or re.match(r"^['`=\(\)\|\!\-\@\~\"\&\/\\\^\$].*?", form.search.data) or re.match(r".*?['`=\(\)\|\!\-\@\~\"\&\/\\\^\$]$", form.search.data):
        return render_template('404.html', form=form, sitename=sitename)
    query = re.sub(r"['`=\(\)\|\!\@\~\"\&\/\\\^\$]", r"", form.search.data)
    query = re.sub(r"(-+)", r"-", query)
    query = ' '.join(query.encode('utf-8').lower().split())
    sensitivewordslist = sensitivewords()
    for word in sensitivewordslist:
        if word.search(query):
            return render_template('wordnotallowed.html', form=form, sitename=sitename)
    return redirect(url_for('search_results', query=query, category=0, order=0, page=1))

@app.route('/to-<info_hash>.html', methods=['GET', 'POST'])
@cache.cached(timeout=60*1,key_prefix=make_cache_key)
def detail(info_hash):
    form = SearchForm()
    conn,curr = sphinx_conn()
    detailsql = 'SELECT * FROM film WHERE info_hash=%s'
    curr.execute(detailsql, [info_hash])
    hash = curr.fetchone()
    tags = Search_Tags.query.order_by(Search_Tags.id.desc()).limit(30)
    actors = Search_Actors.query.order_by(Search_Actors.id.desc()).limit(30)

    sphinx_close(curr,conn)
    if not hash:
        return render_template('404.html', form=form, sitename=sitename)
    if Complaint.query.filter_by(info_hash=info_hash).first():
        return render_template('complaintdetail.html', form=form, tags=tags, hash=hash, keywords=keywords,
                               actors=actors, sitename=sitename)
    return render_template('detail.html', form=form, tags=tags, hash=hash, sitename=sitename)

@app.route('/rm_maglink/<info_hash>.html', methods=['GET', 'POST'])
def dmca(info_hash):
    if Complaint.query.filter_by(info_hash=info_hash).first():
        return redirect(url_for('index'))
    complaintform = ComplaintForm()
    form=SearchForm()
    conn,curr = sphinx_conn()
    querysql = 'SELECT * FROM film WHERE info_hash=%s'
    curr.execute(querysql, [info_hash])
    thishash = curr.fetchone()
    sphinx_close(curr,conn)
    complaintform.info_hash.data = info_hash
    if complaintform.validate_on_submit():
        hash = complaintform.info_hash.data
        reason = complaintform.reason.data
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newcomplaint = Complaint(
            info_hash=hash, reason=reason, create_time=create_time)
        db.session.add(newcomplaint)
        db.session.commit()
        return render_template('dmcaok.html', form=form, sitename=sitename)
    return render_template('dmca.html', form=form, complaintform=complaintform, thishash=thishash, sitename=sitename)

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.errorhandler(404)
def notfound(e):
    form = SearchForm()
    return render_template('404.html', form=form, sitename=sitename)

@manager.command
def init_db():
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    manager.run()