# [C] rok Python ProxyShare can be used as an SSRF proxy through absolute URL paths

## Summary
Severity: Critical
Advisory: GHSA-jh67-hwqw-m5r7
CVE: CVE-2026-45568
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-jh67-hwqw-m5r7
Type: github-advisory

## Affected
- PyPI: `zrok` — affected >=0.4.47

## Details
## Summary

Alice exposes a Python SDK `ProxyShare` with a fixed target URL. Bob sends a request to the share with an absolute URL in the path. The Flask handler passes that path to `urllib.parse.urljoin`, which replaces Alice's configured target host with Bob's host and returns the server-side response to Bob.

## Details

The Python SDK proxy route accepts every path under the share:

```python
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
```

It constructs the outbound URL with `urljoin` and then sends the request:

```python
url = urllib.parse.urljoin(self.target, path)
resp = requests.request(
    method=request.method,
    url=url,
    headers={key: value for (key, value) in request.headers
             if key.lower() not in HOP_BY_HOP_HEADERS},
    data=request.get_data(),
    cookies=request.cookies,
    allow_redirects=False,
    stream=True,
    verify=self.verify_ssl
)
```

When `path` is `[http://127.0.0.1:19190/metadata`](http://127.0.0.1:19190/metadata%60), `urljoin(self.target, path)` returns `[http://127.0.0.1:19190/metadata`](http://127.0.0.1:19190/metadata%60). The proxy sends the request to Bob's chosen URL rather than Alice's target.

## References
- https://github.com/openziti/zrok/security/advisories/GHSA-jh67-hwqw-m5r7
- https://github.com/openziti/zrok
