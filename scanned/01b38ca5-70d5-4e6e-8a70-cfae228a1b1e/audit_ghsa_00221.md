# [M] Improper date handling in Django

## Summary
Severity: Medium
Advisory: GHSA-7wph-fc4w-wqp2
CVE: CVE-2010-4535
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-7wph-fc4w-wqp2
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.1.3
- PyPI: `Django` — affected >=1.2 <1.2.4

## Details
The password reset functionality in django.contrib.auth in Django before 1.1.3, 1.2.x before 1.2.4, and 1.3.x before 1.3 beta 1 does not validate the length of a string representing a base36 timestamp, which allows remote attackers to cause a denial of service (resource consumption) via a URL that specifies a large base36 integer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4535
- https://github.com/django/django/commit/7f8dd9cbac074389af8d8fd235bf2cb657227b9a
- https://github.com/django/django/commit/d5d8942a160685c403d381a279e72e09de5489a9
- https://bugzilla.redhat.com/show_bug.cgi?id=665373
- https://github.com/advisories/GHSA-7wph-fc4w-wqp2
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-29.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-9.yaml
- https://web.archive.org/web/20200228193349/http://www.securityfocus.com/bid/45563
- http://code.djangoproject.com/changeset/15032
- http://lists.fedoraproject.org/pipermail/package-announce/2011-January/053041.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-January/053072.html
- http://secunia.com/advisories/42715
- http://secunia.com/advisories/42827
- http://secunia.com/advisories/42913
- http://www.djangoproject.com/weblog/2010/dec/22/security
- http://www.openwall.com/lists/oss-security/2010/12/23/4
- http://www.openwall.com/lists/oss-security/2011/01/03/5
- http://www.securityfocus.com/bid/45563
- http://www.ubuntu.com/usn/USN-1040-1
