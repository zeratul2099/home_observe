import pytz
from flask import Flask, url_for, render_template
from sqlalchemy import desc
from common import get_host_shortname, get_database
app = Flask(__name__)


@app.route('/')
@app.route('/<hostname>')
def main(hostname=None):
    cet = pytz.timezone('CET')
    log = get_database()
    select = log.select().order_by(desc(log.c.timestamp))
    if hostname:
        select = select.where(log.c.hostname.contains(hostname))
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
    return render_template('webgui.html', result=result, hostname=hostname)


with app.test_request_context():
    url_for('static', filename='styles.css')

if __name__ == '__main__':
    app.run()

