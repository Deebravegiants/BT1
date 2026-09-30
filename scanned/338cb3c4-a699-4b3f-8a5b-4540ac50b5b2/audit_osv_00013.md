# [M] ALPINE-CVE-2014-9913

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2014-9913
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-9913
Type: osv

## Affected
- Alpine:v3.10: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.11: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.12: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.13: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.14: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.15: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.16: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.17: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.18: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.19: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.20: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.21: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.22: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.23: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.24: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.5: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.6: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.7: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.8: `unzip` — affected >=0 <6.0-r3
- Alpine:v3.9: `unzip` — affected >=0 <6.0-r3

## Details
Buffer overflow in the list_files function in list.c in Info-Zip UnZip 6.0 allows remote attackers to cause a denial of service (crash) via vectors related to the compression method.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-9913
