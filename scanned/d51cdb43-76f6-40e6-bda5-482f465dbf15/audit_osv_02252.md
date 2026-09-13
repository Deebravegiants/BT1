# [C] ALPINE-CVE-2021-36159

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-36159
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36159
Type: osv

## Affected
- Alpine:v3.10: `apk-tools` — affected >=0 <2.10.7-r0
- Alpine:v3.11: `apk-tools` — affected >=0 <2.10.7-r0
- Alpine:v3.12: `apk-tools` — affected >=0 <2.10.7-r0
- Alpine:v3.13: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.14: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.15: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.16: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.17: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.18: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.19: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.20: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.21: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.22: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.23: `apk-tools` — affected >=0 <2.12.6-r0
- Alpine:v3.24: `apk-tools` — affected >=0 <2.12.6-r0

## Details
libfetch before 2021-07-26, as used in apk-tools, xbps, and other products, mishandles numeric strings for the FTP and HTTP protocols. The FTP passive mode implementation allows an out-of-bounds read because strtol is used to parse the relevant numbers into address bytes. It does not check if the line ends prematurely. If it does, the for-loop condition checks for the '\0' terminator one byte too late.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36159
