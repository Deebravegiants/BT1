# [H] ALPINE-CVE-2020-25125

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25125
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25125
Type: osv

## Affected
- Alpine:v3.12: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.13: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.14: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.15: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.16: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.17: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.18: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.19: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.20: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.21: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.22: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.23: `gnupg` — affected >=0 <2.2.23-r0
- Alpine:v3.24: `gnupg` — affected >=0 <2.2.23-r0

## Details
GnuPG 2.2.21 and 2.2.22 (and Gpg4win 3.1.12) has an array overflow, leading to a crash or possibly unspecified other impact, when a victim imports an attacker's OpenPGP key, and this key has AEAD preferences. The overflow is caused by a g10/key-check.c error. NOTE: GnuPG 2.3.x is unaffected. GnuPG 2.2.23 is a fixed version.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25125
