# [H] ALPINE-CVE-2025-68973

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-68973
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68973
Type: osv

## Affected
- Alpine:v3.20: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.21: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.22: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.23: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.24: `gnupg` — affected >=0 <2.4.9-r0

## Details
In GnuPG before 2.4.9, armor_filter in g10/armor.c has two increments of an index variable where one is intended, leading to an out-of-bounds write for crafted input. (For ExtendedLTS, 2.2.51 and later are fixed versions.)

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68973
