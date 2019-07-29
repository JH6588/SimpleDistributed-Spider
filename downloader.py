import socket
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, urlsplit



DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
DEFAULT_DELAY = 1
DEFAULT_RETRIES = 2
DEFAULT_TIMEOUT = 60
DEFAULT_ENCODING = "utf8"


class Downloader:
    proxies = None

    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, num_retries=DEFAULT_RETRIES,
                 timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING, request_verify=None):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.num_retries = num_retries
        self.timeout = timeout
        self.encoding = encoding
        self.request_verify = request_verify
        self.req_proxies = None

    def change_proxy(self):
        return None

    def __call__(self, url):
        self.throttle.wait(url)
        headers = {'User-agent': self.user_agent}

        result = self.download(url, headers=headers, num_retries=self.num_retries)

        return result['html']

    def download(self, url, headers, num_retries, data=None, method='GET', req=requests):

        proxies = {urlparse(url).scheme: Downloader.proxies}
        print(proxies, "--------")
        try:
            if method == 'POST':
                res = req.post(url, proxies=proxies, headers=headers, timeout=self.timeout, data=data,

                               verify=self.request_verify)
            else:
                res = req.get(url, proxies=proxies, headers=headers, timeout=self.timeout, data=data,
                              verify=self.request_verify)
                # print(res.headers)
            res.encoding = self.encoding
            html = res.text
            # print(html)
            if not self.result__testing(html):  # 对所得到源码进行检测。
                raise Exception("can not pass the result testing")
            code = res.status_code

            return {"html": html, "code": code}
        except Exception as e:
            print('download error', e)
            if num_retries > 1:
                time.sleep(5)
                Downloader.proxies = self.change_proxy()  # 换ip

                return self.download(url, headers=headers, num_retries=num_retries - 1)
            else:

                raise Exception("Exception : download error  more than {} times ".format(self.num_retries))

    def result__testing(self, html):
        return True


class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """

    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
