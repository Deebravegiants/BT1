# [H] Potential SQL injection via QuerySet.order_by and FilteredRelation

## Summary
Severity: High
Advisory: BIT-django-2026-1312
Aliases: CVE-2026-1312, GHSA-6426-9fv3-65x8, PYSEC-2026-47
Ecosystem: Bitnami
Published: 2026-02-05
Source: https://osv.dev/vulnerability/BIT-django-2026-1312
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.2

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.
`.QuerySet.order_by()` is subject to SQL injection in column aliases containing periods when the same alias is, using a suitably crafted dictionary, with dictionary expansion, used in `FilteredRelation`.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Solomon Kebede for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-1312
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
- https://access.redhat.com/security/cve/CVE-2026-1312
- https://bugzilla.redhat.com/show_bug.cgi?id=2436342
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1312.json
