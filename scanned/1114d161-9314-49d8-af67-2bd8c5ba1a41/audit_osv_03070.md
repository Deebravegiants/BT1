# [H] ALPINE-CVE-2024-37676

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-37676
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-37676
Type: osv

## Affected
- Alpine:v3.22: `htop` — affected >=0 <3.4.1-r1
- Alpine:v3.23: `htop` — affected >=0 <3.4.1-r2
- Alpine:v3.24: `htop` — affected >=0 <3.5.3-r0

## Details
An issue in htop-dev htop v.2.20 allows a local attacker to cause an out-of-bounds access in the Header_populateFromSettings function.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-37676
