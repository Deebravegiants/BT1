# [H] ALPINE-CVE-2018-10858

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10858
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10858
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.11: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.12: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.13: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.14: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.15: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.16: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.17: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.18: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.19: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.20: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.21: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.22: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.23: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.24: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.5: `samba` — affected >=4.7.0 <4.5.16-r1
- Alpine:v3.6: `samba` — affected >=4.7.0 <4.6.16-r0
- Alpine:v3.7: `samba` — affected >=4.7.0 <4.7.6-r1
- Alpine:v3.8: `samba` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.9: `samba` — affected >=4.7.0 <4.8.4-r0

## Details
A heap-buffer overflow was found in the way samba clients processed extra long filename in a directory listing. A malicious samba server could use this flaw to cause arbitrary code execution on a samba client. Samba versions before 4.6.16, 4.7.9 and 4.8.4 are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10858
