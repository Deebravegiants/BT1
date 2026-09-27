# [M] ALPINE-CVE-2019-12308

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12308
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12308
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.21-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.21-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.21-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.21-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.21-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.21-r0

## Details
An issue was discovered in Django 1.11 before 1.11.21, 2.1 before 2.1.9, and 2.2 before 2.2.2. The clickable Current URL value displayed by the AdminURLFieldWidget displays the provided value without validating it as a safe URL. Thus, an unvalidated value stored in the database, or a value provided as a URL query parameter payload, could result in an clickable JavaScript link.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12308
