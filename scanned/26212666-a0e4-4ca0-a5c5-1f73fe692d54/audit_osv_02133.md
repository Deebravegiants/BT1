# [C] ALPINE-CVE-2021-26937

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-26937
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-26937
Type: osv

## Affected
- Alpine:v3.10: `screen` — affected >=0 <4.6.2-r2
- Alpine:v3.11: `screen` — affected >=0 <4.7.0-r2
- Alpine:v3.12: `screen` — affected >=0 <4.8.0-r1
- Alpine:v3.13: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.14: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.15: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.16: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.17: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.18: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.19: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.20: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.21: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.22: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.23: `screen` — affected >=0 <4.8.0-r4
- Alpine:v3.24: `screen` — affected >=0 <4.8.0-r4

## Details
encoding.c in GNU Screen through 4.8.0 allows remote attackers to cause a denial of service (invalid write access and application crash) or possibly have unspecified other impact via a crafted UTF-8 character sequence.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-26937
