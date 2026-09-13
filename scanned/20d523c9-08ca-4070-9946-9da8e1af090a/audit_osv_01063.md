# [M] ALPINE-CVE-2018-18384

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-18384
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18384
Type: osv

## Affected
- Alpine:v3.11: `unzip` — affected >=0 <6.0-r7
- Alpine:v3.12: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.13: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.14: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.15: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.16: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.17: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.18: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.19: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.20: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.21: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.22: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.23: `unzip` — affected >=0 <6.0-r9
- Alpine:v3.24: `unzip` — affected >=0 <6.0-r9

## Details
Info-ZIP UnZip 6.0 has a buffer overflow in list.c, when a ZIP archive has a crafted relationship between the compressed-size value and the uncompressed-size value, because a buffer size is 10 and is supposed to be 12.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18384
