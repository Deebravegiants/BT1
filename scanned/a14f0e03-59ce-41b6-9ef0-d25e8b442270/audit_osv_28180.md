# [H] django-wiki denial of service via regular expression

## Summary
Severity: High
Advisory: CVE-2024-28865
Aliases: GHSA-wj85-w4f4-xh8h, PYSEC-2026-2049
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-28865
Type: osv

## Details
django-wiki is a wiki system for Django. Installations of django-wiki prior to version 0.10.1 are vulnerable to maliciously crafted article content that can cause severe use of server CPU through a regular expression loop. Version 0.10.1 fixes this issue. As a workaround, close off access to create and edit articles by anonymous users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28865.json
- https://github.com/django-wiki/django-wiki/security/advisories/GHSA-wj85-w4f4-xh8h
- https://nvd.nist.gov/vuln/detail/CVE-2024-28865
- https://github.com/django-wiki/django-wiki/commit/8e280fd6c0bd27ce847c67b2d216c6cbf920f88c
