# [H] Cross Site Scripting vulnerability in django-jsonform's admin form.

## Summary
Severity: High
Advisory: GHSA-x9jp-4w8m-4f3c
CWE: CWE-79, CWE-80
Ecosystem: PyPI
Published: 2022-06-10
Source: https://github.com/advisories/GHSA-x9jp-4w8m-4f3c
Type: github-advisory

## Affected
- PyPI: `django-jsonform` — affected >=0 <2.10.1

## Details
### Description

django-jsonform stores the raw JSON data of the db field in a hidden textarea on the admin page. However, that data was kept in the textarea after unescaping it using the `safe` template filter. This opens up possibilities for XSS attacks.

This only affects the admin pages where the django-jsonform is rendered.

### Mitigation

Upgrade to django-jsonform version 2.10.1 or later.

### For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/bhch/django-jsonform/issues).
* Email the maintainer at `Bharat Chauhan <tell.bhch@gmail.com>`.

## References
- https://github.com/bhch/django-jsonform/security/advisories/GHSA-x9jp-4w8m-4f3c
- https://github.com/bhch/django-jsonform
