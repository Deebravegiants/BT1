# [M] ALPINE-CVE-2019-3498

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-3498
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3498
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.18-r0
- Alpine:v3.6: `py-django` — affected >=0 <1.11.18-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.18-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.18-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.18-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.18-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.18-r0

## Details
In Django 1.11.x before 1.11.18, 2.0.x before 2.0.10, and 2.1.x before 2.1.5, an Improper Neutralization of Special Elements in Output Used by a Downstream Component issue exists in django.views.defaults.page_not_found(), leading to content spoofing (in a 404 error page) if a user fails to recognize that a crafted URL has malicious content.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3498
