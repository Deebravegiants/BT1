# [H] django-sendfile2 before 0.7.0 contains reflected file download vulnerability

## Summary
Severity: High
Advisory: GHSA-pcjh-6r5h-r92r
CWE: CWE-20
Ecosystem: PyPI
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-pcjh-6r5h-r92r
Type: github-advisory

## Affected
- PyPI: `django-sendfile2` — affected >=0 <0.7.0

## Details
Similar to CVE-2022-36359 for Django, django-sendfile2 did not protect against a reflected file download attack in version 0.6.1 and earlier. If the file name used by django-sendfile2 was derived from user input, then it would be possible to perform a such an attack. A new version of django-sendfile2 will be released. Either download django-sendfile2 0.7.0 as a workaround or sanitize user input yourself, using Django's patch as a template: https://github.com/django/django/commit/bd062445cffd3f6cc6dcd20d13e2abed818fa173

## References
- https://github.com/moggers87/django-sendfile2/security/advisories/GHSA-pcjh-6r5h-r92r
- https://github.com/moggers87/django-sendfile2/commit/4c370859023292e3715200a57843f86c5ef3cd77
- https://github.com/moggers87/django-sendfile2
- https://github.com/moggers87/django-sendfile2/releases/tag/v0.7.0
