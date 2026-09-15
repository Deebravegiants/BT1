# [H] ALPINE-CVE-2019-14459

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14459
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14459
Type: osv

## Affected
- Alpine:v3.10: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.11: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.12: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.13: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.14: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.15: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.16: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.17: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.18: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.19: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.20: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.21: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.22: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.23: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.24: `nfdump` — affected >=0 <1.6.18-r0
- Alpine:v3.7: `nfdump` — affected >=0 <1.6.15-r1
- Alpine:v3.8: `nfdump` — affected >=0 <1.6.17-r1
- Alpine:v3.9: `nfdump` — affected >=0 <1.6.18-r0

## Details
nfdump 1.6.17 and earlier is affected by an integer overflow in the function Process_ipfix_template_withdraw in ipfix.c that can be abused in order to crash the process remotely (denial of service).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14459
