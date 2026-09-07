# [M] Cross-site scripting in django

## Summary
Severity: Medium
Advisory: GHSA-8m3r-rv5g-fcpq
CVE: CVE-2011-0697
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-8m3r-rv5g-fcpq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.1 <1.1.4
- PyPI: `Django` — affected >=1.2 <1.2.5

## Details
Cross-site scripting (XSS) vulnerability in Django 1.1.x before 1.1.4 and 1.2.x before 1.2.5 might allow remote attackers to inject arbitrary web script or HTML via a filename associated with a file upload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0697
- https://github.com/django/django/commit/1966786d2dde73e17f39cf340eb33fcb5d73904e
- https://github.com/django/django/commit/1f814a9547842dcfabdae09573055984af9d3fab
- https://github.com/django/django/commit/90be6ca20d607977dec234ec972b77b83955749b
- https://github.com/django/django/commit/a9cf3d23724ff6918103e86aa863eadd1fab811d
- https://bugzilla.redhat.com/show_bug.cgi?id=676359
- https://github.com/advisories/GHSA-8m3r-rv5g-fcpq
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-11.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-31.yaml
- https://web.archive.org/web/20110521033259/http://secunia.com/advisories/43230
- https://web.archive.org/web/20110521033304/http://secunia.com/advisories/43297
- https://web.archive.org/web/20110521033309/http://secunia.com/advisories/43382
- https://web.archive.org/web/20110521033314/http://secunia.com/advisories/43426
- https://web.archive.org/web/20130616104703/http://www.securityfocus.com/bid/46296
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054207.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054208.html
- http://openwall.com/lists/oss-security/2011/02/09/6
- http://secunia.com/advisories/43230
- http://secunia.com/advisories/43297
