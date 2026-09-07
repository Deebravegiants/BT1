# [M] Moderate severity vulnerability that affects Zope2

## Summary
Severity: Medium
Advisory: GHSA-v7q8-wvvh-c97p
CVE: CVE-2010-1104
CWE: CWE-79
Ecosystem: PyPI
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-v7q8-wvvh-c97p
Type: github-advisory

## Affected
- PyPI: `Zope2` — affected >=2.8.0 <2.8.12
- PyPI: `Zope2` — affected >=2.9.0 <2.9.12
- PyPI: `Zope2` — affected >=2.10.0 <2.10.11
- PyPI: `Zope2` — affected >=2.11.0 <2.11.6
- PyPI: `Zope2` — affected >=2.12.0 <2.12.3

## Details
Cross-site scripting (XSS) vulnerability in Zope 2.8.x before 2.8.12, 2.9.x before 2.9.12, 2.10.x before 2.10.11, 2.11.x before 2.11.6, and 2.12.x before 2.12.3 allows remote attackers to inject arbitrary web script or HTML via vectors related to error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1104
- https://exchange.xforce.ibmcloud.com/vulnerabilities/55599
- https://github.com/advisories/GHSA-v7q8-wvvh-c97p
- https://mail.zope.org/pipermail/zope-announce/2010-January/002229.html
- http://secunia.com/advisories/38007
- http://www.osvdb.org/61655
- http://www.securityfocus.com/bid/37765
- http://www.vupen.com/english/advisories/2010/0104
