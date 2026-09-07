# [H] Django Allows Arbitrary URL Generation

## Summary
Severity: High
Advisory: GHSA-2655-q453-22f9
CVE: CVE-2012-4520
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2655-q453-22f9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.3 <1.3.4
- PyPI: `Django` — affected >=1.4 <1.4.2

## Details
The `django.http.HttpRequest.get_host` function in Django 1.3.x before 1.3.4 and 1.4.x before 1.4.2 allows remote attackers to generate and display arbitrary URLs via crafted username and password Host header values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4520
- https://github.com/django/django/commit/92d3430f12171f16f566c9050c40feefb830a4a3
- https://github.com/django/django/commit/9305c0e12d43c4df999c3301a1f0c742264a657e
- https://github.com/django/django/commit/b45c377f8f488955e0c7069cad3f3dd21910b071
- https://www.openwall.com/lists/oss-security/2012/10/30/4
- https://www.djangoproject.com/weblog/2012/oct/17/security
- https://www.debian.org/security/2013/dsa-2634
- https://web.archive.org/web/20140417023920/http://securitytracker.com/id?1027708
- https://ubuntu.com/usn/usn-1757-1
- https://ubuntu.com/usn/usn-1632-1
- https://lists.fedoraproject.org/pipermail/package-announce/2012-October/090970.html
- https://lists.fedoraproject.org/pipermail/package-announce/2012-October/090904.html
- https://lists.fedoraproject.org/pipermail/package-announce/2012-October/090666.html
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2012-7.yaml
- https://github.com/django/django
- https://bugzilla.redhat.com/show_bug.cgi?id=865164
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=691145
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=691145
- http://lists.fedoraproject.org/pipermail/package-announce/2012-October/090666.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-October/090904.html
