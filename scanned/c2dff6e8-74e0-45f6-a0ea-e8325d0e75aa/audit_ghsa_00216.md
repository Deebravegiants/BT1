# [H] Improper query string handling in Django

## Summary
Severity: High
Advisory: GHSA-fwr5-q9rx-294f
CVE: CVE-2010-4534
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-fwr5-q9rx-294f
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.1.3
- PyPI: `Django` — affected >=1.2 <1.2.4

## Details
The administrative interface in django.contrib.admin in Django before 1.1.3, 1.2.x before 1.2.4, and 1.3.x before 1.3 beta 1 does not properly restrict use of the query string to perform certain object filtering, which allows remote authenticated users to obtain sensitive information via a series of requests containing regular expressions, as demonstrated by a created_by__password__regex parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4534
- https://github.com/django/django/commit/17084839fd7e267da5729f2a27753322b9d415a0
- https://github.com/django/django/commit/85207a245bf09fdebe486b4c7bbcb65300f2a693
- https://bugzilla.redhat.com/show_bug.cgi?id=665373
- https://github.com/advisories/GHSA-fwr5-q9rx-294f
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-28.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-8.yaml
- http://archives.neohapsis.com/archives/fulldisclosure/2010-12/0580.html
- http://code.djangoproject.com/changeset/15031
- http://evilpacket.net/2010/dec/22/information-leakage-django-administrative-interfac
- http://lists.fedoraproject.org/pipermail/package-announce/2011-January/053041.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-January/053072.html
- http://ngenuity-is.com/advisories/2010/dec/22/information-leakage-in-django-administrative-inter
- http://secunia.com/advisories/42715
- http://secunia.com/advisories/42827
- http://secunia.com/advisories/42913
- http://www.djangoproject.com/weblog/2010/dec/22/security
- http://www.openwall.com/lists/oss-security/2010/12/23/4
- http://www.openwall.com/lists/oss-security/2011/01/03/5
