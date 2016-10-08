import pytz
from flask import Flask, url_for, render_template, request
from sqlalchemy import desc, func, select as select_stm
from common import get_host_shortname, get_database
app = Flask(__name__)


@app.route('/')
@app.route('/<hostname>')
def main(hostname=None):
    page = request.args.get('page')
    if page is None:
        page = '0'
    pagesize = 50
    cet = pytz.timezone('CET')
    log = get_database()
    select = log.select().order_by(desc(log.c.timestamp))
    count = select_stm([func.count()]).select_from(log)
    if hostname:
        select = select.where(log.c.hostname.contains(hostname))
        count = count.where(log.c.hostname.contains(hostname))
    if page != 'all':
        count = count.execute().fetchone()[0]
        maxpages = count // pagesize
        print(page)
        select = select.limit(pagesize)
        select = select.offset(int(page) * pagesize)
    else:
        maxpages = None
    rows = select.execute()
    result = list()
    for row in rows.fetchall():
        entry = dict(
            shortname = get_host_shortname(row.hostname),
            status = 'Online' if row.status == 1 else 'Offline',
            timestamp = pytz.utc.localize(row.timestamp).astimezone(cet).strftime('%d.%m.%Y %H:%M:%S'),
            ipv4 = row.ipv4,
            ipv6 = row.ipv6,
        )
        result.append(entry)
    return render_template('webgui.html', result=result, hostname=hostname, page=page, maxpages=maxpages)


with app.test_request_context():
    url_for('static', filename='styles.css')

if __name__ == '__main__':
    app.run()

