# [M]  Django: GDALRaster may over-read heap memory when constructed from bytes

## Summary
Severity: Medium
Advisory: GHSA-crhf-3pfg-w68w
CVE: CVE-2026-53877
CWE: CWE-805
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-crhf-3pfg-w68w
Type: github-advisory

## Affected
- PyPI: `django` — affected >=0 <5.2.16
- PyPI: `django` — affected >=6.0.0 <6.0.7

## Details
An issue was discovered in Django 6.0 before 6.0.7 and 5.2 before 5.2.16.
`django.contrib.gis.gdal.GDALRaster` over-reads its in-memory buffer when constructed from a bytes object, which can disclose adjacent memory or cause service degradation via a potential segmentation fault when the `vsi_buffer` property is accessed.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Bence Nagy for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53877
- https://github.com/django/django/commit/38dfbd27d7d4f4e6eaa087d7a90f2613fbf55b3a
- https://github.com/django/django/commit/6c66eb8cec52b303af85c2c6e4dd00aa37654dbc
- https://github.com/django/django/commit/6ca2bbe2efce21010eff48f1f36a3f621d698ed8
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-2091.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/jul/07/security-releases
