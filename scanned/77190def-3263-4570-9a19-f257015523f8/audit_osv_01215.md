# [H] ALPINE-CVE-2018-6188

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6188
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6188
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.10-r0
- Alpine:v3.6: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.10-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.10-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.10-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.10-r0

## Details
django.contrib.auth.forms.AuthenticationForm in Django 2.0 before 2.0.2, and 1.11.8 and 1.11.9, allows remote attackers to obtain potentially sensitive information by leveraging data exposure from the confirm_login_allowed() method, as demonstrated by discovering whether a user account is inactive.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6188
