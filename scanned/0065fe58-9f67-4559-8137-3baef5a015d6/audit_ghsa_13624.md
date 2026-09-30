# [M] twisted.web has disordered HTTP pipeline response

## Summary
Severity: Medium
Advisory: GHSA-xc8x-vp79-p3wm
CVE: CVE-2023-46137
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-xc8x-vp79-p3wm
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0 <23.10.0rc1

## Details
Twisted is an event-based framework for internet applications. Prior to version 23.10.0rc1, when sending multiple HTTP requests in one TCP packet, twisted.web will process the requests asynchronously without guaranteeing the response order. If one of the endpoints is controlled by an attacker, the attacker can delay the response on purpose to manipulate the response of the second request when a victim launched two requests using HTTP pipeline. Version 23.10.0rc1 contains a patch for this issue.

### Details
There's an example faulty program:
```python
from twisted.internet import reactor, endpoints
from twisted.web import server
from twisted.web.proxy import ReverseProxyResource
from twisted.web.resource import Resource

class Second(Resource):
    isLeaf = True
    def render_GET(self, request):
        return b'SECOND\n'

class First(Resource):
    isLeaf = True
    def render_GET(self, request):
        def send_response():
            request.write(b'FIRST DELAYED\n')
            request.finish()
        reactor.callLater(0.5, send_response)
        return server.NOT_DONE_YET

root = Resource()

root.putChild(b'second', Second())
root.putChild(b'first', First())

endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
endpoint.listen(server.Site(root))
reactor.run()
```

When two requests for `/first` and `/second` are sent in the same order, the second request will be responded to first.
```shell
echo -en "GET /first HTTP/1.1\r\nHost: a\r\n\r\nGET /second HTTP/1.1\r\nHost: a\r\n\r\n" | nc localhost 8080
```

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-xc8x-vp79-p3wm
- https://nvd.nist.gov/vuln/detail/CVE-2023-46137
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2023-224.yaml
- https://github.com/twisted/twisted
- https://lists.debian.org/debian-lts-announce/2024/11/msg00028.html
