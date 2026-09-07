# [M] Zope Server vulnerable to DoS via header injection

## Summary
Severity: Medium
Advisory: GHSA-vwrc-g9q6-f675
CVE: CVE-2002-0687
CWE: CWE-400
Ecosystem: PyPI
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-vwrc-g9q6-f675
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=2.0.0 <2.4.4b2
- PyPI: `zope` — affected >=2.5.0 <2.5.1b2

## Details
Zope is a Web application server for Linux. Zope versions 2.0 through 2.5.1 b1 are vulnerable to a denial of service attack, caused by a vulnerability that occurs when using the "through the Web code" capability. A remote attacker could inject malicious headers into a response to cause the vulnerable system to crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-0687
- https://marc.info/?l=zope-announce&m=101890177815066&w=2
- https://marc.info/?l=zope-announce&m=101897461507941&w=2
- https://marc.info/?l=zope-announce&m=101897462107967&w=2
- https://web.archive.org/web/20020822024423/http://www.iss.net/security_center/static/9621.php
- https://web.archive.org/web/20021018100409/http://online.securityfocus.com/bid/5813
- http://www.redhat.com/support/errata/RHSA-2002-060.html
- http://www.zope.org/Products/Zope/Hotfix_2002-04-15/security_alert
