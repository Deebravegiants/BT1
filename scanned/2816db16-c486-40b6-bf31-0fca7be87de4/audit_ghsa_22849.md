# [H] Django DoS in django.views.static.serve

## Summary
Severity: High
Advisory: GHSA-jhjg-w2cp-5j44
CVE: CVE-2015-0221
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jhjg-w2cp-5j44
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.18
- PyPI: `Django` — affected >=1.6 <1.6.10
- PyPI: `Django` — affected >=1.7 <1.7.3

## Details
The `django.views.static.serve` view in Django before 1.4.18, 1.6.x before 1.6.10, and 1.7.x before 1.7.3 reads files an entire line at a time, which allows remote attackers to cause a denial of service (memory consumption) via a long line in a file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0221
- https://github.com/django/django/commit/553779c4055e8742cc832ed525b9ee34b174934f
- https://github.com/django/django/commit/818e59a3f0fbadf6c447754d202d88df025f8f2a
- https://github.com/django/django/commit/d020da6646c5142bc092247d218a3d1ce3e993f7
- https://github.com/django/django
- https://github.com/django/django/blob/9b9c805cedb08621bd5dc58a01a6478eb7cc49a9/docs/releases/1.4.18.txt#L48C1-L49C1
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-6.yaml
- https://web.archive.org/web/20150128111656/http://secunia.com/advisories/62285
- https://web.archive.org/web/20150128111656/http://secunia.com/advisories/62309
- https://web.archive.org/web/20150523054951/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2015:109/?name=MDVSA-2015:109
- https://web.archive.org/web/20150523054953/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2015:036/?name=MDVSA-2015:036
- https://web.archive.org/web/20151104201446/http://secunia.com/advisories/62718
- https://www.djangoproject.com/weblog/2015/jan/13/security
- http://advisories.mageia.org/MGASA-2015-0026.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148485.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148608.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148696.html
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00001.html
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00035.html
- http://ubuntu.com/usn/usn-2469-1
