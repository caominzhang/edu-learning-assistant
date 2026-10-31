#!/usr/bin/env python3
"""家庭学习档案 v0.1：本地单用户 Web 应用。无需云服务。"""
import csv, io, json, os, re, sqlite3, uuid, html, base64, hmac, math
from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from email.parser import BytesParser
from email.policy import default

ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('TRACKER_DATA',ROOT/'data'))
UPLOADS=DATA/'uploads'; UPLOADS.mkdir(parents=True,exist_ok=True)
DB=DATA/'records.sqlite3'
HOST=os.environ.get('TRACKER_HOST','127.0.0.1'); PORT=int(os.environ.get('TRACKER_PORT','8765'))
TARGET=os.environ.get('TRACKER_STUDENT','示例同学').strip()
VERSION='0.2.0-preview.1'
PASSWORD=os.environ.get('TRACKER_PASSWORD','')
if HOST not in ('127.0.0.1','localhost','::1') and len(PASSWORD)<16:
 raise RuntimeError('局域网部署必须设置至少16位 TRACKER_PASSWORD')

def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript('''CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,day TEXT NOT NULL,subject TEXT NOT NULL,kind TEXT NOT NULL,title TEXT NOT NULL,score REAL,max_score REAL,rank_num INTEGER,class_size INTEGER,note TEXT DEFAULT '',image_name TEXT DEFAULT '',match_status TEXT DEFAULT '未检测',created_at TEXT NOT NULL); CREATE INDEX IF NOT EXISTS idx_events_day ON events(day);''')
 return c
conn().close()

def esc(x): return html.escape(str(x or ''),quote=True)
def num(v,typ=float):
 if v is None or str(v).strip()=='':return None
 result=typ(v)
 if not math.isfinite(result):raise ValueError('数值必须为有限数字')
 return result

def recognize(path):
 try:
  from PIL import Image,ImageOps,ImageEnhance
  import pytesseract
  im=Image.open(path); im=ImageOps.exif_transpose(im).convert('RGB')
  if max(im.size)>2400: im.thumbnail((2400,2400))
  txt=pytesseract.image_to_string(ImageEnhance.Contrast(im).enhance(1.5),lang='chi_sim+eng',config='--psm 11',timeout=35)
  compact=re.sub(r'\s+','',txt)
  if TARGET in compact:status='疑似匹配（OCR）'
  elif len(TARGET)>=3 and any(TARGET[i:i+2] in compact for i in range(len(TARGET)-1)):status='疑似匹配（部分姓名）'
  else:status='未识别到（不能排除）'
  return status,txt[:12000]
 except Exception as e:return '识别未运行',f'本机OCR不可用：{e}。可以手工确认姓名。'

HTML='''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>家庭学习档案</title><style>
:root{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:#18212d;background:#f4f6fa}*{box-sizing:border-box}body{margin:0}.wrap{max-width:1100px;margin:auto;padding:26px 18px}h1{font-size:26px;margin:0 0 5px}h2{font-size:19px}p{color:#64748b}nav{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}nav a,.btn{background:#1d4ed8;color:white;text-decoration:none;border:0;border-radius:9px;padding:10px 15px;cursor:pointer;font-size:14px}nav a{background:#e4eaf5;color:#183456}.panel{background:white;border-radius:15px;padding:20px;margin:16px 0;box-shadow:0 1px 8px #15233d12}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}label{font-size:13px;color:#475569;display:block;margin:8px 0 4px}input,select,textarea{width:100%;padding:10px;border:1px solid #d4dbe7;border-radius:8px;font:inherit}textarea{min-height:75px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:11px 8px;text-align:left;border-bottom:1px solid #e6ebf2}th{color:#64748b}small,.muted{color:#64748b}img.preview{max-width:100%;max-height:380px;border-radius:8px}.scroll{overflow:auto}.danger{color:#b91c1c}.chip{background:#eef2ff;border-radius:12px;padding:4px 9px;font-size:12px}button.secondary{background:#e8edf5;color:#273449}.stat{font-size:26px;font-weight:700;margin:8px 0}.notice{background:#fff7df;padding:12px;border-radius:8px;color:#78510d}</style></head><body><main class="wrap"><h1>家庭学习档案</h1><p>本地运行 · 成绩统计为主 · 表扬记录与姓名识别为附加功能 · 目标学生：__TARGET__</p><nav><a href="/">总览</a><a href="/new">新增记录</a><a href="/records">全部记录</a><a href="/export.csv">导出 CSV</a></nav>__CONTENT__</main></body></html>'''

def page(body):return HTML.replace('__TARGET__',esc(TARGET)).replace('__CONTENT__',body).encode()

def form(values=None,extra=''):
 v=values or {}; d=esc(v.get('day',datetime.now().date().isoformat())); kind=v.get('kind','成绩')
 options=''.join(f'<option {"selected" if kind==k else ""}>{k}</option>' for k in ('成绩','表扬','作业','其他'))
 return f'''<section class="panel"><h2>新增学习记录</h2><form action="/save" method="post" enctype="multipart/form-data"><div class="grid"><div><label>日期 *</label><input name="day" type="date" required value="{d}"></div><div><label>科目 *</label><select name="subject"><option>数学</option><option>语文</option><option>英语</option><option>物理</option><option>历史</option><option>其他</option></select></div><div><label>记录类型</label><select name="kind">{options}</select></div><div><label>项目/标题 *</label><input name="title" required placeholder="例如：病句专项测试 / 数学课堂笔记"></div><div><label>得分（可空）</label><input type="number" step="0.01" name="score"></div><div><label>满分（可空）</label><input type="number" step="0.01" name="max_score"></div><div><label>班级排名（可空）</label><input type="number" min="1" name="rank_num"></div><div><label>参与人数（可空）</label><input type="number" min="1" name="class_size"></div></div><label>老师原话 / 备注</label><textarea name="note" placeholder="例如：表扬以上同学，数学大卷课堂笔记记得很认真"></textarea><label>原始图片（可选，JPG/PNG/WEBP，最多12MB）</label><input type="file" name="photo" accept="image/jpeg,image/png,image/webp"><p class="muted">上传后会尝试本地 OCR；OCR 不可靠，须手动确认。空白成绩请留空，不要填 0。</p><button class="btn">保存记录</button></form></section>{extra}'''

class Handler(BaseHTTPRequestHandler):
 def send(self,data,status=200,mime='text/html; charset=utf-8',headers=None):
  self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store')
  for k,v in (headers or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(data)
 def redirect(self,path):self.send(b'',303,headers={'Location':path})
 def authorized(self):
  if not PASSWORD:return True
  try:
   encoded=self.headers.get('Authorization','')
   if not encoded.startswith('Basic '):raise ValueError()
   account,secret=base64.b64decode(encoded[6:],validate=True).decode().split(':',1)
   if account=='admin' and hmac.compare_digest(secret.encode(),PASSWORD.encode()):return True
  except (ValueError,UnicodeError):pass
  self.send(b'Authentication required',401,headers={'WWW-Authenticate':'Basic realm="Learning Assistant", charset="UTF-8"'})
  return False
 def valid_origin(self):
  origin=self.headers.get('Origin')
  host=self.headers.get('Host','')
  if origin and (urlparse(origin).netloc!=host or urlparse(origin).scheme not in ('http','https')):
   self.send(b'Invalid origin',403);return False
  if self.headers.get('Sec-Fetch-Site')=='cross-site':
   self.send(b'Invalid origin',403);return False
  return True
 def do_GET(self):
  if not self.authorized():return
  path=urlparse(self.path).path;c=conn()
  try:
   if path=='/new':return self.send(page(form()))
   if path=='/':
    a=c.execute('SELECT COUNT(*) n,COUNT(score) scored,SUM(CASE WHEN kind="表扬" THEN 1 ELSE 0 END) praises FROM events').fetchone()
    rows=c.execute('SELECT * FROM events ORDER BY day DESC,id DESC LIMIT 12').fetchall()
    subjects=c.execute('SELECT subject,COUNT(*) n,ROUND(AVG(CASE WHEN score IS NOT NULL AND max_score>0 THEN score*100.0/max_score END),1) pct FROM events GROUP BY subject ORDER BY n DESC').fetchall()
    body=f'''<div class="grid"><section class="panel"><small>累计记录</small><div class="stat">{a['n']}</div></section><section class="panel"><small>有分数的记录</small><div class="stat">{a['scored']}</div></section><section class="panel"><small>表扬记录</small><div class="stat">{a['praises'] or 0}</div></section></div><section class="panel"><h2>各科汇总</h2><div class="scroll"><table><tr><th>科目</th><th>记录数</th><th>平均得分率（有满分的记录）</th></tr>{''.join(f"<tr><td>{esc(x['subject'])}</td><td>{x['n']}</td><td>{str(x['pct'])+'%' if x['pct'] is not None else '—'}</td></tr>" for x in subjects)}</table></div></section><section class="panel"><h2>最近记录</h2>{self.table(rows)}</section>'''
    return self.send(page(body))
   if path=='/records':return self.send(page('<section class="panel"><h2>全部记录</h2>'+self.table(c.execute('SELECT * FROM events ORDER BY day DESC,id DESC').fetchall())+'</section>'))
   if path=='/export.csv':
    s=io.StringIO();w=csv.writer(s);w.writerow(['日期','科目','类型','标题','得分','满分','排名','人数','备注','姓名识别状态','原图文件'])
    for r in c.execute('SELECT * FROM events ORDER BY day,id'):w.writerow([r[k] for k in ('day','subject','kind','title','score','max_score','rank_num','class_size','note','match_status','image_name')])
    return self.send(('\ufeff'+s.getvalue()).encode('utf-8'),mime='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="learning_records.csv"'})
   if path.startswith('/image/'):
    name=path.split('/')[-1]
    if not re.fullmatch(r'[0-9a-f]{32}\.(jpg|png|webp)',name):return self.send(b'Not found',404)
    p=UPLOADS/name
    if not p.is_file():return self.send(b'Not found',404)
    return self.send(p.read_bytes(),mime={'jpg':'image/jpeg','png':'image/png','webp':'image/webp'}[p.suffix[1:]])
   if path.startswith('/record/'):
    rid=int(path.split('/')[-1]);r=c.execute('SELECT * FROM events WHERE id=?',(rid,)).fetchone()
    if not r:return self.send(page('记录不存在'),404)
    img=f'<p><img class="preview" src="/image/{esc(r["image_name"])}"></p>' if r['image_name'] else ''
    opts=''.join(f'<option {"selected" if r["match_status"]==x else ""}>{x}</option>' for x in ('已人工确认出现','已人工确认未出现','疑似匹配（OCR）','疑似匹配（部分姓名）','未识别到（不能排除）','识别未运行','未检测'))
    body=f'''<section class="panel"><h2>{esc(r['title'])}</h2><p>{esc(r['day'])} · {esc(r['subject'])} · {esc(r['kind'])}</p><p>得分：{esc(r['score']) or '—'} / {esc(r['max_score']) or '—'}；排名：{esc(r['rank_num']) or '—'}</p><p>{esc(r['note'])}</p>{img}<form method="post" action="/confirm"><input type="hidden" name="id" value="{rid}"><label>姓名识别状态（请人工核对原图）</label><select name="status">{opts}</select><button class="btn" style="margin-top:10px">更新确认状态</button></form></section>'''
    return self.send(page(body))
   return self.send(page('页面不存在'),404)
  finally:c.close()
 def table(self,rows):
  return '<div class="scroll"><table><tr><th>日期</th><th>科目</th><th>类型</th><th>项目</th><th>得分</th><th>得分率</th><th>排名</th><th>姓名状态</th></tr>'+''.join(f'''<tr><td>{esc(r['day'])}</td><td>{esc(r['subject'])}</td><td>{esc(r['kind'])}</td><td><a href="/record/{r['id']}">{esc(r['title'])}</a></td><td>{esc(r['score']) if r['score'] is not None else '—'}{('/'+esc(r['max_score'])) if r['max_score'] is not None else ''}</td><td>{round(r['score']/r['max_score']*100,1)}%''' + f'''</td><td>{esc(r['rank_num']) or '—'}</td><td><small>{esc(r['match_status'])}</small></td></tr>''' if r['score'] is not None and r['max_score'] and r['max_score']>0 else f'''<tr><td>{esc(r['day'])}</td><td>{esc(r['subject'])}</td><td>{esc(r['kind'])}</td><td><a href="/record/{r['id']}">{esc(r['title'])}</a></td><td>{esc(r['score']) if r['score'] is not None else '—'}</td><td>—</td><td>{esc(r['rank_num']) or '—'}</td><td><small>{esc(r['match_status'])}</small></td></tr>''' for r in rows)+'</table></div>'
 def parse_form(self):
  self.connection.settimeout(45)
  n=int(self.headers.get('Content-Length','0'))
  if n<0:raise ValueError('无效请求长度')
  if n>13*1024*1024:raise ValueError('提交文件过大')
  raw=self.rfile.read(n);typ=self.headers.get('Content-Type','')
  if 'multipart/form-data' in typ:
   msg=BytesParser(policy=default).parsebytes(b'Content-Type: '+typ.encode()+b'\r\nMIME-Version: 1.0\r\n\r\n'+raw)
   data={};photo=None
   for part in msg.iter_parts():
    key=part.get_param('name',header='content-disposition');filename=part.get_filename()
    if filename and key=='photo':photo=(filename,part.get_payload(decode=True))
    elif key:data[key]=part.get_payload(decode=True).decode('utf-8',errors='replace')
   return data,photo
  return {k:v[0] for k,v in parse_qs(raw.decode(),keep_blank_values=True).items()},None
 def do_POST(self):
  if not self.authorized() or not self.valid_origin():return
  try:
   d,photo=self.parse_form();c=conn()
   try:
    if self.path=='/confirm':
     allowed=('已人工确认出现','已人工确认未出现','疑似匹配（OCR）','疑似匹配（部分姓名）','未识别到（不能排除）','识别未运行','未检测')
     if d.get('status') not in allowed:raise ValueError('无效状态')
     rid=int(d['id']);c.execute('UPDATE events SET match_status=? WHERE id=?',(d['status'],rid));c.commit();return self.redirect('/record/'+str(rid))
    if self.path!='/save':return self.send(page('不存在'),404)
    day=d.get('day','');datetime.strptime(day,'%Y-%m-%d')
    title=d.get('title','').strip();subject=d.get('subject','').strip();kind=d.get('kind','成绩')
    if not title or not subject or kind not in ('成绩','表扬','作业','其他'):raise ValueError('请填写标题、科目和类型')
    score=num(d.get('score'));maximum=num(d.get('max_score'));rank=num(d.get('rank_num'),int);class_size=num(d.get('class_size'),int)
    if maximum is not None and maximum<=0:raise ValueError('满分必须大于0')
    if score is not None and score<0:raise ValueError('得分不能为负')
    if maximum is not None and score is not None and score>maximum:raise ValueError('得分不能超过满分')
    if rank is not None and rank<1:raise ValueError('排名必须大于0')
    if class_size is not None and class_size<1:raise ValueError('人数必须大于0')
    if rank is not None and class_size is not None and rank>class_size:raise ValueError('排名不能大于参与人数')
    image_name='';status='未检测';ocr=''
    if photo and photo[1]:
     name,blob=photo
     if len(blob)>12*1024*1024:raise ValueError('图片超过12MB')
     from PIL import Image
     im=Image.open(io.BytesIO(blob));fmt=im.format
     if fmt not in ('JPEG','PNG','WEBP'):raise ValueError('仅支持 JPG/PNG/WEBP 图片')
     ext={'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt];image_name=uuid.uuid4().hex+'.'+ext
     dest=UPLOADS/image_name;dest.write_bytes(blob)
     status,ocr=recognize(dest)
    note=d.get('note','')[:5000]
    if ocr:note+=('\n\n[OCR参考文本，未经核实]\n'+ocr[:3000])
    cur=c.execute('INSERT INTO events(day,subject,kind,title,score,max_score,rank_num,class_size,note,image_name,match_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(day,subject,kind,title,score,maximum,rank,class_size,note,image_name,status,datetime.now().isoformat(timespec='seconds')));c.commit()
    return self.redirect('/record/'+str(cur.lastrowid))
   finally:c.close()
  except Exception as e:self.send(page('<section class="panel"><h2>保存失败</h2><p class="danger">'+esc(e)+'</p><a href="/new">返回录入</a></section>'),400)

def run():
 print(f'家庭学习档案已启动：http://{HOST}:{PORT}  数据目录：{DATA}',flush=True)
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

if __name__=='__main__':
 run()
