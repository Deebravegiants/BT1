# [H] ALPINE-CVE-2023-43787

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-43787
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43787
Type: osv

## Affected
- Alpine:v3.16: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.8.7-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.8.7-r0

## Details
A vulnerability was found in libX11 due to an integer overflow within the XCreateImage() function. This flaw allows a local user to trigger an integer overflow and execute arbitrary code with elevated privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43787
