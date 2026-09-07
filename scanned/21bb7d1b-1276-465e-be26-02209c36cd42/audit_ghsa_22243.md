# [M] Django Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-54qj-48vx-cr9f
CVE: CVE-2008-2302
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-54qj-48vx-cr9f
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.91 <0.91.2
- PyPI: `Django` — affected >=0.95 <0.95.3
- PyPI: `Django` — affected >=0.96 <0.96.2

## Details
Cross-site scripting (XSS) vulnerability in the login form in the administration application in Django 0.91 before 0.91.2, 0.95 before 0.95.3, and 0.96 before 0.96.2 allows remote attackers to inject arbitrary web script or HTML via the URI of a certain previous request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-2302
- https://github.com/django/django/commit/50ce7fb57d79e8940ccf6e2781f2f01df029b5c5
- https://github.com/django/django/commit/6e657e2c404a96e744748209e896d8a69c15fdf2
- https://github.com/django/django/commit/7791e5c050cebf86d868c5dab7092185b125fdc9
- https://exchange.xforce.ibmcloud.com/vulnerabilities/42396
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2008-1.yaml
- https://web.archive.org/web/20080725022008/http://secunia.com/advisories/30291
- https://web.archive.org/web/20081012011038/http://secunia.com/advisories/30250
- https://web.archive.org/web/20170222015451/http://securitytracker.com/id?1020028
- https://web.archive.org/web/20200228153339/http://www.securityfocus.com/bid/29209
- http://www.djangoproject.com/weblog/2008/may/14/security
