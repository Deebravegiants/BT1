# [H] ALPINE-CVE-2015-8948

## Summary
Severity: High
Advisory: ALPINE-CVE-2015-8948
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8948
Type: osv

## Affected
- Alpine:v3.10: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.11: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.12: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.13: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.14: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.15: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.16: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.17: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.18: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.19: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.2: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.20: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.21: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.22: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.23: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.24: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.3: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.4: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.5: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.6: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.7: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.8: `libidn` — affected >=0 <1.33-r0
- Alpine:v3.9: `libidn` — affected >=0 <1.33-r0

## Details
idn in GNU libidn before 1.33 might allow remote attackers to obtain sensitive memory information by reading a zero byte as input, which triggers an out-of-bounds read.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8948
