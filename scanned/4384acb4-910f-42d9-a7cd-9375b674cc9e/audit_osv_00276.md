# [H] ALPINE-CVE-2016-9014

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9014
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9014
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.2: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.3: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.4: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.5: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.6: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.8.16-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.8.16-r0

## Details
Django before 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3, when settings.DEBUG is True, allow remote attackers to conduct DNS rebinding attacks by leveraging failure to validate the HTTP Host header against settings.ALLOWED_HOSTS.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9014
