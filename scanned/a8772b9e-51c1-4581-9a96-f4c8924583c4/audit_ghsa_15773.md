# [M] Twisted vulnerable to HTML injection in HTTP redirect body

## Summary
Severity: Medium
Advisory: GHSA-cf56-g6w6-pqq2
CVE: CVE-2024-41810
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-29
Source: https://github.com/advisories/GHSA-cf56-g6w6-pqq2
Type: github-advisory

## Affected
- PyPI: `twisted` — affected >=0 <24.7.0rc1

## Details
### Summary

The `twisted.web.util.redirectTo` function contains an HTML injection vulnerability. If application code allows an attacker to control the redirect URL this vulnerability may result in Reflected Cross-Site Scripting (XSS) in the redirect response HTML body.

### Details
Twisted’s `redirectTo` function generates an `HTTP 302 Redirect` response. The response contains an HTML body, built for exceptional cases where the browser doesn’t properly handle the redirect, allowing the user to click a link, navigating them to the specified destination.

The function reflects the destination URL in the HTML body without any output encoding. 
```python
# https://github.com/twisted/twisted/blob/trunk/src/twisted/web/_template_util.py#L88
def redirectTo(URL: bytes, request: IRequest) -> bytes:
    # ---snip---
    content = b"""
<html>
    <head>
        <meta http-equiv=\"refresh\" content=\"0;URL=%(url)s\">
    </head>
    <body bgcolor=\"#FFFFFF\" text=\"#000000\">
    <a href=\"%(url)s\">click here</a>
    </body>
</html>
""" % {
        b"url": URL
    }
    return content
```

If an attacker has full or partial control over redirect location due to an application bug, also known as an “Open Redirect”, they may inject arbitrary HTML into the response’s body, ultimately leading to an XSS attack.

It’s worth noting that the issue is known to maintainers and tracked with GitHub [Issue#9839](https://github.com/twisted/twisted/issues/9839). The issue description, however, does not make any mention of exploitability and simply states: “…Browsers don't seem to actually render that page…”

### PoC
The issue can be reproduced by running the following Twisted-based HTTP server locally:
```python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.util import redirectTo

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        url = request.args[b'url'][0]  # <-- open redirect
        return redirectTo(url, request)

site = server.Site(Simple())
reactor.listenTCP(9009, site)
reactor.run()
```
Once running, navigate to the following URL: `http://127.0.0.1:9009?url=ws://example.com/"><script>alert(document.location)</script>`, and verify that the “alert” dialog was displayed.

**Note**: Due to the different ways browsers validate the redirect Location header, this attack is possible only in **Firefox**. All other tested browsers will display an error message to the user and will not render the HTML body.

### Impact
If successfully exploited, the issue will allow malicious JavaScript to run in the context of the victim's session. This will in turn lead to unauthorized access/modification to victim's account and information associated with it, or allow for unauthorized operations to be performed within the context of the victim's session.

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-cf56-g6w6-pqq2
- https://nvd.nist.gov/vuln/detail/CVE-2024-41810
- https://github.com/twisted/twisted/commit/046a164f89a0f08d3239ecebd750360f8914df33
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2024-75.yaml
- https://github.com/twisted/twisted
- https://lists.debian.org/debian-lts-announce/2024/11/msg00028.html
