# [M] Potential denial-of-service vulnerability via nested geometry collections

## Summary
Severity: Medium
Advisory: BIT-django-2026-15830
Aliases: CVE-2026-15830, PYSEC-2026-3717
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-django-2026-15830
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.8

## Details
An issue was discovered in Django 5.2 before 5.2.17 and 6.0 before 6.0.8.
GeoDjango's `django.contrib.gis.geos.GEOSGeometry` is subject to a potential denial-of-service when parsing deeply nested `GEOMETRYCOLLECTION` objects supplied as well-known text (WKT), well-known binary (WKB), or hex-encoded WKB, which triggers unbounded recursion and a segmentation fault in the underlying GEOS library. Spatial field lookups and the `django.contrib.gis.forms.GeometryField` form field are also affected.
Earlier, unsupported Django series (such as 5.1.x, 5.0.x, and 4.2.x) were not evaluated and may also be affected.
Django would like to thank Andrew MacPherson and kimchunbok_ for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://github.com/django/django/commit/6af5da31775417c610dbf9c3f1b5b8333d42daf6
- https://github.com/django/django/commit/9e4a3f186b6b07b483bfd9195ea06734663fcd06
- https://github.com/django/django/commit/ba80833fa656dd09660b97c4429331067db1b080
- https://github.com/django/django/commit/d2e59b77fe18de318a8272c2a7bbc798d84d1d0d
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-15830
- https://www.djangoproject.com/weblog/2026/aug/04/security-releases/
