# [M] Twisted vulnerable to NameVirtualHost Host header injection

## Summary
Severity: Medium
Advisory: GHSA-vg46-2rrj-3647
CVE: CVE-2022-39348
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-vg46-2rrj-3647
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0.9.4 <22.10.0rc1

## Details
When the host header does not match a configured host, `twisted.web.vhost.NameVirtualHost` will return a `NoResource` resource which renders the Host header unescaped into the 404 response allowing HTML and script injection.

Example configuration:
```python
from twisted.web.server import Site
from twisted.web.vhost import NameVirtualHost
from twisted.internet import reactor

resource = NameVirtualHost()
site = Site(resource)
reactor.listenTCP(8080, site)
reactor.run()
```
Output:
```
❯ curl -H"Host:<h1>HELLO THERE</h1>" http://localhost:8080/

<html>
  <head><title>404 - No Such Resource</title></head>
  <body>
    <h1>No Such Resource</h1>
    <p>host b'<h1>hello there</h1>' not in vhost map</p>
  </body>
</html>
```

This vulnerability was introduced in f49041bb67792506d85aeda9cf6157e92f8048f4 and first appeared in the 0.9.4 release.

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-vg46-2rrj-3647
- https://nvd.nist.gov/vuln/detail/CVE-2022-39348
- https://github.com/twisted/twisted/commit/f2f5e81c03f14e253e85fe457e646130780db40b
- https://github.com/twisted/twisted/commit/f49041bb67792506d85aeda9cf6157e92f8048f4
- https://github.com/twisted/twisted
- https://lists.debian.org/debian-lts-announce/2022/11/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00028.html
- https://security.gentoo.org/glsa/202301-02
