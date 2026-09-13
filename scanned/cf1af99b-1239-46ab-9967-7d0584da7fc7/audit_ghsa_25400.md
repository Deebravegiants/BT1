# [C] Zope Object Database (ZODB) vulnerable to arbitrary Python code execution in ZEO storage servers

## Summary
Severity: Critical
Advisory: GHSA-4x83-5gw5-q346
CVE: CVE-2009-0668
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-4x83-5gw5-q346
Type: github-advisory

## Affected
- PyPI: `ZODB3` — affected >=0 <3.8.2

## Details
Unspecified vulnerability in Zope Object Database (ZODB) before 3.8.2, when certain Zope Enterprise Objects (ZEO) database sharing is enabled, allows remote attackers to execute arbitrary Python code via vectors involving the ZEO network protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0668
- https://exchange.xforce.ibmcloud.com/vulnerabilities/52377
- https://github.com/pypa/advisory-database/tree/main/vulns/zodb3/PYSEC-2009-8.yaml
- https://github.com/zopefoundation/ZODB3
- https://web.archive.org/web/20151023102330/http://secunia.com/advisories/36204
- https://web.archive.org/web/20151023102336/http://secunia.com/advisories/36205
- https://web.archive.org/web/20200229152709/http://www.securityfocus.com/bid/35987
- http://mail.zope.org/pipermail/zope-announce/2009-August/002220.html
- http://pypi.python.org/pypi/ZODB3/3.8.2#whats-new-in-zodb-3-8-2
