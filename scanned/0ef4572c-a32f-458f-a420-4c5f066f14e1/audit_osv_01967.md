# [H] ALPINE-CVE-2020-35492

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35492
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35492
Type: osv

## Affected
- Alpine:v3.10: `cairo` — affected >=0 <1.16.0-r3
- Alpine:v3.11: `cairo` — affected >=0 <1.16.0-r3
- Alpine:v3.12: `cairo` — affected >=0 <1.16.0-r3
- Alpine:v3.13: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.14: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.15: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.16: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.17: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.18: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.19: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.20: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.21: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.22: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.23: `cairo` — affected >=0 <1.16.0-r2
- Alpine:v3.24: `cairo` — affected >=0 <1.16.0-r2

## Details
A flaw was found in cairo's image-compositor.c in all versions prior to 1.17.4. This flaw allows an attacker who can provide a crafted input file to cairo's image-compositor (for example, by convincing a user to open a file in an application using cairo, or if an application uses cairo on untrusted input) to cause a stack buffer overflow -> out-of-bounds WRITE. The highest impact from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35492
