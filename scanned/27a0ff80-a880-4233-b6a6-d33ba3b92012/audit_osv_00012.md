# [H] ALPINE-CVE-2014-8141

## Summary
Severity: High
Advisory: ALPINE-CVE-2014-8141
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-8141
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
Heap-based buffer overflow in the getZip64Data function in Info-ZIP UnZip 6.0 and earlier allows remote attackers to execute arbitrary code via a crafted zip file in the -t command argument to the unzip command.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-8141
