# [H] Potential SQL injection via raster lookups on PostGIS

## Summary
Severity: High
Advisory: BIT-django-2026-1207
Aliases: CVE-2026-1207, GHSA-mwm9-4648-f68q, PYSEC-2026-44
Ecosystem: Bitnami
Published: 2026-02-05
Source: https://osv.dev/vulnerability/BIT-django-2026-1207
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.2

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.
Raster lookups on ``RasterField`` (only implemented on PostGIS) allows remote attackers to inject SQL via the band index parameter.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Tarek Nakkouch for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-1207
- https://www.djangoproject.com/weblog/2026/feb/03/security-releases/
- https://access.redhat.com/errata/RHSA-2026:14835
- https://access.redhat.com/errata/RHSA-2026:2694
- https://access.redhat.com/errata/RHSA-2026:3958
- https://access.redhat.com/errata/RHSA-2026:3959
- https://access.redhat.com/errata/RHSA-2026:3960
- https://access.redhat.com/errata/RHSA-2026:3962
- https://access.redhat.com/errata/RHSA-2026:5970
- https://access.redhat.com/errata/RHSA-2026:5971
- https://access.redhat.com/errata/RHSA-2026:6291
- https://access.redhat.com/security/cve/CVE-2026-1207
- https://bugzilla.redhat.com/show_bug.cgi?id=2436338
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1207.json
