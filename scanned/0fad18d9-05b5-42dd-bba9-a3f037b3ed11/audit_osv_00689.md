# [C] ALPINE-CVE-2017-5953

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-5953
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5953
Type: osv

## Affected
- Alpine:v3.10: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.11: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.12: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.13: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.14: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.15: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.16: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.17: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.18: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.19: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.2: `vim` — affected >=0 <7.4.712-r2
- Alpine:v3.20: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.21: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.22: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.23: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.3: `vim` — affected >=0 <7.4.943-r5
- Alpine:v3.4: `vim` — affected >=0 <7.4.1831-r3
- Alpine:v3.5: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.6: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.7: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.8: `vim` — affected >=0 <8.0.0329-r0
- Alpine:v3.9: `vim` — affected >=0 <8.0.0329-r0

## Details
vim before patch 8.0.0322 does not properly validate values for tree length when handling a spell file, which may result in an integer overflow at a memory allocation site and a resultant buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5953
