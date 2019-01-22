import requests
import time
import json
from threading import Thread

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}

class BitmexSpider():

    def __init__(self, stock, interval):
        self.stock = stock
        self.interval = interval
        
    def spider(self):
        try:
            timestamp = int(time.time())//self.interval*self.interval
            r = requests.get('https://www.bitmex.com/api/udf/history?symbol=%s&resolution=1&to=%d&from=%d' %
                            (self.stock.upper(), timestamp, timestamp-7*24*60*60))
            obj = json.loads(r.text)
            obj = [[obj['t'][i], obj['c'][i]] for i in range(len(obj['t'])) if obj['t'][i] % self.interval == 0]
            with open('now/%s' % self.stock, 'w') as f:
                f.write(json.dumps(obj))
            return 1
        except Exception as e:
            print('bitmex_spider_error', e)
            return 0

    def run_thread(self):
        while 1:
            if self.spider():
                time.sleep(self.interval)
            else:
                time.sleep(60)

    def run(self):
        t = Thread(target=self.run_thread)
        t.setDaemon(True)
        t.start()


class HuobiSpider():

    def __init__(self, stock, interval):
        self.stock = stock
        self.interval = interval
        
    def spider(self):
        try:
            r = requests.get('https://api.huobi.pro/market/history/kline?symbol=%s&period=15min&size=2000' % self.stock.lower(), headers=headers)
            obj = json.loads(r.text)['data']
            obj = [[obj[-i]['id'], obj[-i]['close']] for i in range(1, len(obj)+1)]
            with open('now/%s' % self.stock, 'w') as f:
                f.write(json.dumps(obj))
            return 1
        except Exception as e:
            print('huobi_spider_error', e)
            return 0

    def run_thread(self):
        while 1:
            if self.spider():
                time.sleep(self.interval)
            else:
                time.sleep(60)

    def run(self):
        t = Thread(target=self.run_thread)
        t.setDaemon(True)
        t.start()

if __name__ == "__main__":
    a = HuobiSpider('btcusdt', 600)
    a.run()
    input()
