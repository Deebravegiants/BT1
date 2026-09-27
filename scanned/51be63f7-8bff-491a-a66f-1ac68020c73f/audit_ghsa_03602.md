# [H] Django allows unintended model editing

## Summary
Severity: High
Advisory: GHSA-hvmf-r92r-27hr
CVE: CVE-2019-19118
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-12-04
Source: https://github.com/advisories/GHSA-hvmf-r92r-27hr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.1 <2.1.15
- PyPI: `Django` — affected >=2.2 <2.2.8

## Details
Django 2.1 before 2.1.15 and 2.2 before 2.2.8 allows unintended model editing. A Django model admin displaying inline related models, where the user has view-only permissions to a parent model but edit permissions to the inline model, would be presented with an editing UI, allowing POST requests, for updating the inline model. Directly editing the view-only parent model was not possible, but the parent model's save() method was called, triggering potential side effects, and causing pre and post-save signal handlers to be invoked. (To resolve this, the Django admin is adjusted to require edit permissions on the parent model in order for inline models to be editable.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19118
- https://github.com/django/django/commit/103ebe2b5ff1b2614b85a52c239f471904d26244
- https://github.com/django/django/commit/36f580a17f0b3cb087deadf3b65eea024f479c21
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-hvmf-r92r-27hr
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-15.yaml
- https://groups.google.com/forum/#!topic/django-announce/GjGqDvtNmWQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6R4HD22PVEVQ45H2JA2NXH443AYJOPL5
- https://security.gentoo.org/glsa/202004-17
- https://security.netapp.com/advisory/ntap-20191217-0003
- https://www.djangoproject.com/weblog/2019/dec/02/security-releases
- http://www.openwall.com/lists/oss-security/2019/12/02/1
