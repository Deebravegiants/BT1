# [M] Django cross-site scripting (XSS) attack via user-supplied redirect URLs

## Summary
Severity: Medium
Advisory: GHSA-7fq8-4pv5-5w5c
CVE: CVE-2015-2317
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7fq8-4pv5-5w5c
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.20
- PyPI: `Django` — affected >=1.5 <1.6.11
- PyPI: `Django` — affected >=1.7 <1.7.7
- PyPI: `Django` — affected >=1.8a1 <1.8c1

## Details
The utils.http.is_safe_url function in Django before 1.4.20, 1.5.x, 1.6.x before 1.6.11, 1.7.x before 1.7.7, and 1.8.x before 1.8c1 does not properly validate URLs, which allows remote attackers to conduct cross-site scripting (XSS) attacks via a control character in a URL, as demonstrated by a \x08javascript: URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2317
- https://github.com/django/django/commit/2342693b31f740a422abf7267c53b4e7bc487c1b
- https://github.com/django/django/commit/2a4113dbd532ce952308992633d802dc169a75f1
- https://github.com/django/django/commit/5510f070711540aaa8d3707776cd77494e688ef9
- https://github.com/django/django/commit/770427c2896a078925abfca2317486b284d22f04
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-9.yaml
- https://web.archive.org/web/20200228131706/http://www.securityfocus.com/bid/73319
- https://www.djangoproject.com/weblog/2015/mar/18/security-releases
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/155421.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-June/160263.html
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00001.html
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00035.html
- http://ubuntu.com/usn/usn-2539-1
- http://www.debian.org/security/2015/dsa-3204
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:195
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
