# [M] ALPINE-CVE-2025-68972

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-68972
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68972
Type: osv

## Affected
- Alpine:v3.20: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.21: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.22: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.23: `gnupg` — affected >=0 <2.4.9-r0
- Alpine:v3.24: `gnupg` — affected >=0 <2.4.9-r0

## Details
In GnuPG through 2.4.8, if a signed message has \f at the end of a plaintext line, an adversary can construct a modified message that places additional text after the signed material, such that signature verification of the modified message succeeds (although an "invalid armor" message is printed during verification). This is related to use of \f as a marker to denote truncation of a long plaintext line.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68972
