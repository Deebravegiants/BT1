# [H] ALPINE-CVE-2018-20969

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20969
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20969
Type: osv

## Affected
- Alpine:v3.10: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.11: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.12: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.13: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.14: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.15: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.16: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.17: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.18: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.19: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.20: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.21: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.22: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.23: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.24: `patch` — affected >=0 <2.7.6-r6
- Alpine:v3.9: `patch` — affected >=0 <2.7.6-r6

## Details
do_ed_script in pch.c in GNU patch through 2.7.6 does not block strings beginning with a ! character. NOTE: this is the same commit as for CVE-2019-13638, but the ! syntax is specific to ed, and is unrelated to a shell metacharacter.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20969
