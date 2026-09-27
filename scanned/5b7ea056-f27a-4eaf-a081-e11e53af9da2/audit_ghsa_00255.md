# [C] Directory traversal in Django

## Summary
Severity: Critical
Advisory: GHSA-7g9h-c88w-r7h2
CVE: CVE-2011-0698
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-7g9h-c88w-r7h2
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.1 <1.1.4
- PyPI: `Django` — affected >=1.2 <1.2.5

## Details
Directory traversal vulnerability in Django 1.1.x before 1.1.4 and 1.2.x before 1.2.5 on Windows might allow remote attackers to read or execute files via a / (slash) character in a key in a session cookie, related to session replays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0698
- https://github.com/django/django/commit/194566480b15cf4e294d3f03ff587019b74044b2
- https://github.com/django/django/commit/570a32a047ea56265646217264b0d3dab1a14dbd
- https://github.com/advisories/GHSA-7g9h-c88w-r7h2
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-12.yaml
- https://web.archive.org/web/20110521033259/http://secunia.com/advisories/43230
- https://web.archive.org/web/20130616104703/http://www.securityfocus.com/bid/46296
- http://openwall.com/lists/oss-security/2011/02/09/6
- http://www.djangoproject.com/weblog/2011/feb/08/security
- http://www.mandriva.com/security/advisories?name=MDVSA-2011:031
