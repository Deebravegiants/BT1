# [M] ALPINE-CVE-2025-69277

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-69277
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-69277
Type: osv

## Affected
- Alpine:v3.20: `libsodium` — affected >=0 <1.0.19-r1
- Alpine:v3.21: `libsodium` — affected >=0 <1.0.20-r1
- Alpine:v3.22: `libsodium` — affected >=0 <1.0.20-r1
- Alpine:v3.23: `libsodium` — affected >=0 <1.0.20-r1
- Alpine:v3.24: `libsodium` — affected >=0 <1.0.20-r1

## Details
libsodium before ad3004e, in atypical use cases involving certain custom cryptography or untrusted data to crypto_core_ed25519_is_valid_point, mishandles checks for whether an elliptic curve point is valid because it sometimes allows points that aren't in the main cryptographic group.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-69277
