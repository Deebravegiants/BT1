# [M] Directory traversal outside of SENDFILE_ROOT in django-sendfile2

## Summary
Severity: Medium
Advisory: GHSA-6r3c-8xf3-ggrr
CWE: CWE-22
Ecosystem: PyPI
Published: 2020-06-24
Source: https://github.com/advisories/GHSA-6r3c-8xf3-ggrr
Type: github-advisory

## Affected
- PyPI: `django-sendfile2` — affected >=0 <0.6.0

## Details
django-sendfile2 currently relies on the backend to correctly limit file paths to `SENDFILE_ROOT`. This is not the case for the `simple` and `development` backends, it is also not necessarily the case for any of the other backends either (it's just an assumption that was made by the original author).

This will be fixed in 0.6.0 which is to be released the same day as this advisory is made public.

When upgrading, you will need to make sure `SENDFILE_ROOT` is set in your settings module if it wasn't already.

## References
- https://github.com/moggers87/django-sendfile2/security/advisories/GHSA-6r3c-8xf3-ggrr
- https://github.com/moggers87/django-sendfile2/commit/f870c52398a55b9b5189932dd8caa24efb4bc1e1
- https://github.com/moggers87/django-sendfile2
