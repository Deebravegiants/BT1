# [C] ALPINE-CVE-2019-19844

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-19844
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19844
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.27-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.27-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.27-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.27-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.27-r0

## Details
Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user's email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19844
