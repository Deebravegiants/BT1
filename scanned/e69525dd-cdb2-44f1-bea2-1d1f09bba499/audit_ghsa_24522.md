# [H] Zope Object Database (ZODB) Authentication bypass in ZEO storage servers

## Summary
Severity: High
Advisory: GHSA-5432-c996-hvhj
CVE: CVE-2009-0669
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-5432-c996-hvhj
Type: github-advisory

## Affected
- PyPI: `ZODB3` — affected >=0 <3.8.2

## Details
Zope Object Database (ZODB) before 3.8.2, when certain Zope Enterprise Objects (ZEO) database sharing is enabled, allows remote attackers to bypass authentication via vectors involving the ZEO network protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0669
- https://exchange.xforce.ibmcloud.com/vulnerabilities/52379
- https://github.com/pypa/advisory-database/tree/main/vulns/zodb3/PYSEC-2009-9.yaml
- https://github.com/zopefoundation/ZODB3
- http://mail.zope.org/pipermail/zope-announce/2009-August/002220.html
- http://pypi.python.org/pypi/ZODB3/3.8.2#whats-new-in-zodb-3-8-2
