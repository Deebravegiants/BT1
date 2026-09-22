# [H] ALPINE-CVE-2020-25721

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25721
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25721
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=4.13.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=4.13.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.16: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.17: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.18: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.19: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.20: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.21: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.22: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.23: `samba` — affected >=4.13.0 <4.15.2-r0
- Alpine:v3.24: `samba` — affected >=4.13.0 <4.15.2-r0

## Details
Kerberos acceptors need easy access to stable AD identifiers (eg objectSid). Samba as an AD DC now provides a way for Linux applications to obtain a reliable SID (and samAccountName) in issued tickets.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25721
