from redis.client import Redis
from datetime import datetime as dt
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class CF:
    def __init__(self):
        self.url = f'https://api.cloudflare.com/client/v4/accounts/{os.getenv("CF_ACCOUNT_ID")}/' + \
            f'storage/kv/namespaces/{os.getenv("CF_NAMESPACE_ID")}/values/html'
        self.headers = {'Authorization': f'Bearer {os.getenv("CF_API_TOKEN")}', 'Content-Type': 'application/json'}


class Cache:
    def __init__(self):
        self.ttl_s = 604_800
        self.client = Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            decode_responses=True
        )

    def set_key(self, key, value):
        self.client.set(key, json.dumps(value), ex=self.ttl_s)

    def get_key(self, key):
        return json.loads(self.client.get(key))

    def get_keys(self, keys):
        return [json.loads(s) for s in self.client.mget(keys)]


class Xhtml:
    def __init__(self):
        self.title = 'Portfolio - X'
        self.tabs = []
        self.panes = []
        self.html = '{}'

    @property
    def asdict(self) -> dict:
        return self.__dict__

    def process(self, idx, racer, data):
        body = Tbody(data)
        body.refresh()
        table = Table(tbody=body.code)
        pane = Pane(idx, racer['id'], racer['app'], table.code)
        tab = Tab(racer['app'])
        self.tabs.append(tab.code)
        self.panes.append(pane.code)
        return self

    def refresh(self):
        self.html = f"""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
  <title>{self.title}</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </head>
<body>
  <header>
    <ul class="nav nav-tabs justify-content-center" role="tablist">
      {''.join(self.tabs)}
    </ul>
  </header>
  <div class="container tab-content pt-5" id="pills-tabContent">
  {''.join(self.panes)}
  </div>
</body>
</html>
"""


class Tab:
    def __init__(self, app: str = 'Home'):
        self.code = f"""
        <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#{app}">{app.upper()}</a></li>"""


class Pane:
    def __init__(self, idx=0, account=0, name='Home', table=''):
        self.idx = idx
        # 'show active' if not idx else ''
        self.code = f"""
    <div id="{name}" class="tab-pane fade ">
      <h6>ID: {account}</h6>
      <p class="text-secondary fst-italic">xtb-{name}</p>
      {table}
    </div>
"""


class Table:
    def __init__(self, tbody):
        self.code = f"""
      <table class="table table-hover table-sm">
        <thead>
          <tr class="table-secondary">
            <th>Symbol</th> <th>Type</th> <th>Price</th> <th>Vol</th> <th class="text-end">Profit</th>
          </tr>
        </thead>
        <tbody>
        {tbody}
        </tbody>
      </table>
"""


class Tbody:
    def __init__(self, data: list):
        self.data = data
        self.body = []
        self.code = '    <tr><td colspan="5" class="text-secondary text-center fst-italic">No data.</td></tr>'

    def refresh(self):
        if not self.data:
            return False
        cmd_style = {
            0: {"color": "success", "text": "BUY"},
            1: {"color": "danger", "text": "SELL"},
            -1: {"color": "secondary", "text": "NA"}
        }
        for d in self.data:
            cmd = cmd_style.get(d['cmd'], -1)
            value_style = "danger" if d['profit'] < 0 else "success"
            open_time = dt.fromtimestamp(int(d['open_time'])/1000).strftime('%a %d-%b, %I:%M %p')
            html_order = """
        <tr> <td rowspan="3">{0}</td>
          <td rowspan="3">
            <button type="button" class="btn btn-sm btn-outline-{1} fw-bold" 
              style="--bs-btn-padding-y: .1rem; --bs-btn-padding-x: .1rem; --bs-btn-font-size: .55rem;" disabled>{2}
            </button>
          </td>
          <td>{3}</td><td>{4}</td>
          <td class="fw-bold text-end text-{5}">{6}</td>
        </tr>
        <tr><td colspan="3" class="text-secondary fw-light fst-italic"><small>{7}</small></td></tr>
        <tr>
          <td colspan="3" class="text-secondary fw-light"><small><i>Order: </i>{8}<i> Position: </i>{9}</small></td>
        </tr>
        """.format(
                d['symbol'], cmd['color'], cmd['text'], d['open_price'], d['volume'], value_style, d['profit'],
                open_time, d['order2'], d['position']
            )
            self.body.append(html_order)
        self.code = ''.join(self.body)
        return True


setting = json.load(open('settings.json'))
# __all__ = ["Cache", "Xhtml"]
