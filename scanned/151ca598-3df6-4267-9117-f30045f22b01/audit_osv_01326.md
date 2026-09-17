# [M] ALPINE-CVE-2019-10206

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10206
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10206
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.6.0 <2.8.4-r0
- Alpine:v3.11: `ansible` — affected >=2.6.0 <2.8.4-r0
- Alpine:v3.12: `ansible` — affected >=2.6.0 <2.8.4-r0
- Alpine:v3.7: `ansible` — affected >=2.6.0 <2.4.6.0-r1
- Alpine:v3.8: `ansible` — affected >=2.6.0 <2.6.19-r0
- Alpine:v3.9: `ansible` — affected >=2.6.0 <2.7.13-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.8.4-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.8.4-r0

## Details
ansible-playbook -k and ansible cli tools, all versions 2.8.x before 2.8.4, all 2.7.x before 2.7.13 and all 2.6.x before 2.6.19, prompt passwords by expanding them from templates as they could contain special characters. Passwords should be wrapped to prevent templates trigger and exposing them.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10206
