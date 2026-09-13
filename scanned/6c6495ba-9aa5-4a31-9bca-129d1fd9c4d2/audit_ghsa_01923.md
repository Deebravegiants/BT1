# [M] Header injection possible in Django

## Summary
Severity: Medium
Advisory: GHSA-qm57-vhq3-3fwf
CVE: CVE-2021-32052
CWE: CWE-79, CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-09
Source: https://github.com/advisories/GHSA-qm57-vhq3-3fwf
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.22
- PyPI: `Django` — affected >=3.1 <3.1.10
- PyPI: `Django` — affected >=3.2 <3.2.2

## Details
In Django 2.2 before 2.2.22, 3.1 before 3.1.10, and 3.2 before 3.2.2 (with Python 3.9.5+), URLValidator does not prohibit newlines and tabs (unless the URLField form field is used). If an application uses values with newlines in an HTTP response, header injection can occur. Django itself is unaffected because HttpResponse prohibits newlines in HTTP headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32052
- https://github.com/django/django/commit/e1e81aa1c4427411e3c68facdd761229ffea6f6f
- https://bugzilla.redhat.com/show_bug.cgi?id=1944801
- https://docs.djangoproject.com/en/3.2/releases/security
- https://github.com/advisories/GHSA-qm57-vhq3-3fwf
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-8.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZVKYPHR3TKR2ESWXBPOJEKRO2OSJRZUE
- https://security.netapp.com/advisory/ntap-20210611-0002
- https://www.djangoproject.com/weblog/2021/may/06/security-releases
- http://www.openwall.com/lists/oss-security/2021/05/06/1
