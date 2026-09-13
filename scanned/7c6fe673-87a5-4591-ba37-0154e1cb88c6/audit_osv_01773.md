# [H] ALPINE-CVE-2020-14363

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14363
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14363
Type: osv

## Affected
- Alpine:v3.10: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.11: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.12: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.13: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.14: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.15: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.16: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.6.12-r0
- Alpine:v3.9: `libx11` — affected >=0 <1.6.12-r0

## Details
An integer overflow vulnerability leading to a double-free was found in libX11. This flaw allows a local privileged attacker to cause an application compiled with libX11 to crash, or in some cases, result in arbitrary code execution. The highest threat from this flaw is to confidentiality, integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14363
