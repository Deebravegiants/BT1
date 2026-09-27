# [H] ALPINE-CVE-2019-14233

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14233
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14233
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.23-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.23-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.23-r0

## Details
An issue was discovered in Django 1.11.x before 1.11.23, 2.1.x before 2.1.11, and 2.2.x before 2.2.4. Due to the behaviour of the underlying HTMLParser, django.utils.html.strip_tags would be extremely slow to evaluate certain inputs containing large sequences of nested incomplete HTML entities.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14233
