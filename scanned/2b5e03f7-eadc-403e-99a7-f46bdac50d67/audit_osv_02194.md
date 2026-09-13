# [H] ALPINE-CVE-2021-3156

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3156
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3156
Type: osv

## Affected
- Alpine:v3.10: `sudo` — affected >=1.8.2 <1.9.5p2-r0
- Alpine:v3.11: `sudo` — affected >=1.8.2 <1.8.31-r1
- Alpine:v3.12: `sudo` — affected >=1.8.2 <1.9.5p2-r0
- Alpine:v3.13: `sudo` — affected >=1.8.2 <1.9.5p2-r0
- Alpine:v3.14: `sudo` — affected >=1.8.2 <1.9.5p2-r0
- Alpine:v3.15: `sudo` — affected >=1.8.2 <1.9.5p2-r0

## Details
Sudo before 1.9.5p2 contains an off-by-one error that can result in a heap-based buffer overflow, which allows privilege escalation to root via "sudoedit -s" and a command-line argument that ends with a single backslash character.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3156
