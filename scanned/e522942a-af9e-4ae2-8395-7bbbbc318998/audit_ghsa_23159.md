# [M] Zope Object Database Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j6m4-frxh-p4x8
CVE: CVE-2010-3495
CWE: CWE-362
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j6m4-frxh-p4x8
Type: github-advisory

## Affected
- PyPI: `zodb3` — affected >=0 <3.10.0a2

## Details
Race condition in `ZEO/StorageServer.py` in Zope Object Database (ZODB) before 3.10.0a2 allows remote attackers to cause a denial of service (daemon outage) by establishing and then immediately closing a TCP connection, leading to the accept function having an unexpected return value of None, an unexpected value of None for the address, or an ECONNABORTED, EAGAIN, or EWOULDBLOCK error, a related issue to CVE-2010-3492.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3495
- https://github.com/zopefoundation/ZODB/commit/cfe16277ef1b5bb094dc79da50b0df1ee1537590
- https://bugs.launchpad.net/zodb/+bug/135108
- https://github.com/pypa/advisory-database/tree/main/vulns/zodb3/PYSEC-2010-27.yaml
- https://pypi.org/project/ZODB3/3.10.0a2/#a2-2010-05-04
- https://web.archive.org/web/20111225005929/http://secunia.com/advisories/41755
- http://bugs.python.org/issue6706
- http://lists.opensuse.org/opensuse-security-announce/2010-12/msg00006.html
- http://pypi.python.org/pypi/ZODB3/3.10.0#id1
- http://secunia.com/advisories/41755
- http://www.openwall.com/lists/oss-security/2010/09/09/6
- http://www.openwall.com/lists/oss-security/2010/09/11/2
- http://www.openwall.com/lists/oss-security/2010/09/22/3
- http://www.openwall.com/lists/oss-security/2010/09/24/3
