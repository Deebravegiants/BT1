# [C] ALPINE-CVE-2019-17544

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-17544
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17544
Type: osv

## Affected
- Alpine:v3.10: `aspell` — affected >=0 <0.60.6.1-r14
- Alpine:v3.11: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.12: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.13: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.14: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.15: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.16: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.17: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.18: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.19: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.20: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.21: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.22: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.23: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.24: `aspell` — affected >=0 <0.60.8-r0
- Alpine:v3.7: `aspell` — affected >=0 <0.60.6.1-r13
- Alpine:v3.8: `aspell` — affected >=0 <0.60.6.1-r13
- Alpine:v3.9: `aspell` — affected >=0 <0.60.6.1-r14

## Details
libaspell.a in GNU Aspell before 0.60.8 has a stack-based buffer over-read in acommon::unescape in common/getdata.cpp via an isolated \ character.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17544
