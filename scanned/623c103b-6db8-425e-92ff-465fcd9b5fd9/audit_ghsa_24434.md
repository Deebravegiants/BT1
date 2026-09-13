# [M] Django WSGI Header Spoofing Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7qfw-j7hp-v45g
CVE: CVE-2015-0219
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7qfw-j7hp-v45g
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.18
- PyPI: `Django` — affected >=1.6 <1.6.10
- PyPI: `Django` — affected >=1.7 <1.7.3

## Details
Django before 1.4.18, 1.6.x before 1.6.10, and 1.7.x before 1.7.3 allows remote attackers to spoof WSGI headers by using an `_` (underscore) character instead of a `-` (dash) character in an HTTP header, as demonstrated by an `X-Auth_User` header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0219
- https://github.com/django/django/commit/41b4bc73ee0da7b2e09f4af47fc1fd21144c710f
- https://github.com/django/django/commit/4f6fffc1dc429f1ad428ecf8e6620739e8837450
- https://github.com/django/django/commit/d7597b31d5c03106eeba4be14a33b32a5e25f4ee
- https://github.com/django/daphne/blob/e49c39a4e5fac8ec170dd653641a9e90844fd3f1/daphne/http_protocol.py#L151
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-4.yaml
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
- http://www.ubuntu.com/usn/USN-2469-1
