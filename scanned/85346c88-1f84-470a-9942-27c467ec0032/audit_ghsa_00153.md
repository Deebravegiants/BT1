# [H] Cross-site request forgery in Django

## Summary
Severity: High
Advisory: GHSA-5j2h-h5hg-3wf8
CVE: CVE-2011-0696
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-5j2h-h5hg-3wf8
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.1 <1.1.4
- PyPI: `Django` — affected >=1.2 <1.2.5

## Details
Django 1.1.x before 1.1.4 and 1.2.x before 1.2.5 does not properly validate HTTP requests that contain an X-Requested-With header, which makes it easier for remote attackers to conduct cross-site request forgery (CSRF) attacks via forged AJAX requests that leverage a "combination of browser plugins and redirects," a related issue to CVE-2011-0447.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0696
- https://github.com/django/django/commit/408c5c873ce1437c7eee9544ff279ecbad7e150a
- https://github.com/django/django/commit/818e70344e7193f6ebc73c82ed574e6ce3c91afc
- https://bugzilla.redhat.com/show_bug.cgi?id=676357
- https://github.com/advisories/GHSA-5j2h-h5hg-3wf8
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-10.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-30.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054207.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054208.html
- http://openwall.com/lists/oss-security/2011/02/09/6
- http://secunia.com/advisories/43230
- http://secunia.com/advisories/43297
- http://secunia.com/advisories/43382
- http://secunia.com/advisories/43426
- http://www.debian.org/security/2011/dsa-2163
- http://www.djangoproject.com/weblog/2011/feb/08/security
- http://www.mandriva.com/security/advisories?name=MDVSA-2011:031
- http://www.securityfocus.com/bid/46296
- http://www.ubuntu.com/usn/USN-1066-1
