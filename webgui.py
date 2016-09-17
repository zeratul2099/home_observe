from flask import Flask, url_for
from sqlalchemy import desc
from common import get_host_shortname, get_database
app = Flask(__name__)


@app.route('/')
def main():
    log = get_database()
    select = log.select().order_by(desc(log.c.timestamp))
    rows = select.execute()
    result = '<html><head>'
    result += '<link rel="stylesheet" type="text/css" href="/static/styles.css" >'
    result += '</head><body><div id="content_container" class="content"><table>'
    for row in rows.fetchall():
        entry = dict(
            shortname = get_host_shortname(row.hostname),
            status = 'Online' if row.status == 1 else 'Offline',
            timestamp = row.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
            ipv4 = row.ipv4,
            ipv6 = row.ipv6,
        )
        result += '<tr>'
        result += ('<td>{shortname:20s}</td><td>{status}</td><td>{timestamp}</td><td>{ipv4:15}</td><td>{ipv6}</td>'.format(**entry))
        result += '</tr>'
    result += '</table></div></body></html>'
    return result


with app.test_request_context():
    url_for('static', filename='styles.css')

if __name__ == '__main__':
    app.run()

