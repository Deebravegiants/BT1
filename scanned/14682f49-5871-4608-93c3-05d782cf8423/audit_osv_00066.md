# [H] ALPINE-CVE-2016-1248

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-1248
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-1248
Type: osv

## Affected
- Alpine:v3.10: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.11: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.12: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.13: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.14: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.15: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.16: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.17: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.18: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.19: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.2: `vim` — affected >=0 <7.4.712-r1
- Alpine:v3.20: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.21: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.22: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.23: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.3: `vim` — affected >=0 <7.4.943-r4
- Alpine:v3.4: `vim` — affected >=0 <7.4.1831-r2
- Alpine:v3.5: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.6: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.7: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.8: `vim` — affected >=0 <8.0.0056-r0
- Alpine:v3.9: `vim` — affected >=0 <8.0.0056-r0

## Details
vim before patch 8.0.0056 does not properly validate values for the 'filetype', 'syntax' and 'keymap' options, which may result in the execution of arbitrary code if a file with a specially crafted modeline is opened.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-1248
