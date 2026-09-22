# [H] ALPINE-CVE-2020-24584

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-24584
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-24584
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.29-r1
- Alpine:v3.9: `py-django` — affected >=0 <1.11.29-r1
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.29-r1
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.29-r1

## Details
An issue was discovered in Django 2.2 before 2.2.16, 3.0 before 3.0.10, and 3.1 before 3.1.1 (when Python 3.7+ is used). The intermediate-level directories of the filesystem cache had the system's standard umask rather than 0o077.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-24584
