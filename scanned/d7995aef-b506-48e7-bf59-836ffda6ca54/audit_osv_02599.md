# [M] ALPINE-CVE-2022-34903

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-34903
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-34903
Type: osv

## Affected
- Alpine:v3.13: `gnupg` — affected >=0 <2.2.31-r1
- Alpine:v3.14: `gnupg` — affected >=0 <2.2.31-r1
- Alpine:v3.15: `gnupg` — affected >=0 <2.2.31-r2
- Alpine:v3.16: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.17: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.18: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.19: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.20: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.21: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.22: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.23: `gnupg` — affected >=0 <2.2.35-r4
- Alpine:v3.24: `gnupg` — affected >=0 <2.2.35-r4

## Details
GnuPG through 2.3.6, in unusual situations where an attacker possesses any secret-key information from a victim's keyring and other constraints (e.g., use of GPGME) are met, allows signature forgery via injection into the status line.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-34903
