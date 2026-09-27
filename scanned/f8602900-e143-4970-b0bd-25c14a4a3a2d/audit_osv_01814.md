# [M] ALPINE-CVE-2020-16289

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-16289
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-16289
Type: osv

## Affected
- Alpine:v3.13: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.14: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.15: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.16: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.17: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.18: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <9.51-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <9.51-r0

## Details
A buffer overflow vulnerability in cif_print_page() in devices/gdevcif.c of Artifex Software GhostScript v9.50 allows a remote attacker to cause a denial of service via a crafted PDF file. This is fixed in v9.51.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-16289
