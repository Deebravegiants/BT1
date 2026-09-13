# [C] SQL Injection in Django

## Summary
Severity: Critical
Advisory: GHSA-6r97-cj55-9hrq
CVE: CVE-2019-14234
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-08-16
Source: https://github.com/advisories/GHSA-6r97-cj55-9hrq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.11a1 <1.11.23
- PyPI: `Django` — affected >=2.1a1 <2.1.11
- PyPI: `Django` — affected >=2.2a1 <2.2.4

## Details
An issue was discovered in Django 1.11.x before 1.11.23, 2.1.x before 2.1.11, and 2.2.x before 2.2.4. Due to an error in shallow key transformation, key and index lookups for django.contrib.postgres.fields.JSONField, and key lookups for django.contrib.postgres.fields.HStoreField, were subject to SQL injection. This could, for example, be exploited via crafted use of "OR 1=1" in a key or index name to return all records, using a suitably crafted dictionary, with dictionary expansion, as the **kwargs passed to the QuerySet.filter() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14234
- https://github.com/django/django/commit/4f5b58f5cd3c57fee9972ab074f8dc6895d8f387
- https://github.com/django/django/commit/ed682a24fca774818542757651bfba576c3fc3ef
- https://github.com/django/django/commit/f74b3ae3628c26e1b4f8db3d13a91d52a833a975
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-6r97-cj55-9hrq
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-13.yaml
- https://groups.google.com/forum/#!topic/django-announce/jIoju2-KLDs
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/STVX7X7IDWAH5SKE6MBMY3TEI6ZODBTK
- https://seclists.org/bugtraq/2019/Aug/15
- https://security.gentoo.org/glsa/202004-17
- https://security.netapp.com/advisory/ntap-20190828-0002
- https://www.debian.org/security/2019/dsa-4498
- https://www.djangoproject.com/weblog/2019/aug/01/security-releases
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00025.html
