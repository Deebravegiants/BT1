# [H] Django Denial-of-service in strip_tags()

## Summary
Severity: High
Advisory: GHSA-h5jv-4p7w-64jg
CVE: CVE-2019-14233
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-08-06
Source: https://github.com/advisories/GHSA-h5jv-4p7w-64jg
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.11a1 <1.11.23
- PyPI: `Django` — affected >=2.1a1 <2.1.11
- PyPI: `Django` — affected >=2.2a1 <2.2.4

## Details
An issue was discovered in Django 1.11.x before 1.11.23, 2.1.x before 2.1.11, and 2.2.x before 2.2.4. Due to the behaviour of the underlying HTMLParser, django.utils.html.strip_tags would be extremely slow to evaluate certain inputs containing large sequences of nested incomplete HTML entities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14233
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-h5jv-4p7w-64jg
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-12.yaml
- https://groups.google.com/forum/#!topic/django-announce/jIoju2-KLDs
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/STVX7X7IDWAH5SKE6MBMY3TEI6ZODBTK
- https://seclists.org/bugtraq/2019/Aug/15
- https://security.gentoo.org/glsa/202004-17
- https://security.netapp.com/advisory/ntap-20190828-0002
- https://www.debian.org/security/2019/dsa-4498
- https://www.djangoproject.com/weblog/2019/aug/01/security-releases
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00025.html
