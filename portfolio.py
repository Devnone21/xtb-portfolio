from _init import *
racers = setting.get('racers')


def get_trades_rec(_id):
    cache = Cache()
    if not cache.client.exists(f"trades_cur:{_id}"):
        return []
    cur = cache.get_key(f"trades_cur:{_id}")
    rec = list(cur.values())
    rec.sort(key=lambda v: (v['symbol'], v['open_time']))
    return rec


def run():
    x = Xhtml()
    for i, r in enumerate(racers):
        data = get_trades_rec(r['id'])
        x.process(i, r, data)
    x.refresh()

    # push to Cloudflare KV
    cf = CF()
    import requests
    r = requests.put(cf.url, data=x.html, headers=cf.headers)
    print(r)


if __name__ == "__main__":
    run()
