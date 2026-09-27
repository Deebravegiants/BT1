# [H] ALPINE-CVE-2018-1000156

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000156
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000156
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
- Alpine:v3.7: `patch` — affected >=0 <2.7.6-r0
- Alpine:v3.8: `patch` — affected >=0 <2.7.6-r4
- Alpine:v3.9: `patch` — affected >=0 <2.7.6-r6

## Details
GNU Patch version 2.7.6 contains an input validation vulnerability when processing patch files, specifically the EDITOR_PROGRAM invocation (using ed) can result in code execution. This attack appear to be exploitable via a patch file processed via the patch utility. This is similar to FreeBSD's CVE-2015-1418 however although they share a common ancestry the code bases have diverged over time.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000156
