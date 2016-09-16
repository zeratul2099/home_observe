from flask import Flask
from sqlalchemy import desc
from common import get_host_shortname, get_database
app = Flask(__name__)


@app.route('/')
def main():
    log = get_database()
    select = log.select().order_by(desc(log.c.timestamp))
    rows = select.execute()
    result = '<html><body><table>'
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
    result += '</table></body></html>'
    return result


if __name__ == '__main__':
    app.run()

