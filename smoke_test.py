"""Isolated HTTP checks. Does not read or write family data."""
import base64
import importlib
import os
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request

with tempfile.TemporaryDirectory() as data:
    os.environ.update(TRACKER_DATA=data, TRACKER_STUDENT='测试同学',
                      TRACKER_HOST='127.0.0.1', TRACKER_PASSWORD='test-password-123456')
    app = importlib.import_module('app')
    server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_address[1]}'
    auth = 'Basic ' + base64.b64encode(b'admin:test-password-123456').decode()
    def request(path, form=None, authorized=True, origin=None):
        headers = {'Authorization': auth} if authorized else {}
        if origin: headers['Origin'] = origin
        body = urllib.parse.urlencode(form).encode() if form is not None else None
        req = urllib.request.Request(url + path, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return response.status, response.read().decode('utf-8-sig')
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode()
    try:
        assert request('/', authorized=False)[0] == 401
        assert '测试同学' in request('/')[1]
        row = dict(day='2026-11-01', subject='数学', kind='成绩', title='模拟测试', score='90', max_score='100', rank_num='3', class_size='40')
        assert request('/save', row)[0] == 200
        assert '90.0' in request('/export.csv')[1]
        assert request('/confirm', {'id': '1', 'status': '已人工确认出现'})[0] == 200
        assert '已人工确认出现' in request('/record/1')[1]
        assert request('/save', row, origin='https://outside.invalid')[0] == 403
        for changes in ({'score':'nan'}, {'score':'inf'}, {'class_size':'-1'}, {'rank_num':'41'}):
            assert request('/save', dict(row, **changes))[0] == 400
        with app.conn() as db:
            assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 1
        print('PASS: auth, configured name, save, confirmation, export, cross-site rejection, numeric validation, isolated data')
    finally:
        server.shutdown()
        server.server_close()
