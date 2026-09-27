# [M] CVE-2020-11735

## Summary
Severity: Medium
Advisory: CVE-2020-11735
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-25
Source: https://osv.dev/vulnerability/CVE-2020-11735
Type: osv

## Details
The private-key operations in ecc.c in wolfSSL before 4.4.0 do not use a constant-time modular inverse when mapping to affine coordinates, aka a "projective coordinates leak."

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.4.0-stable
- https://github.com/wolfSSL/wolfssl/commit/1de07da61f0c8e9926dcbd68119f73230dae283f
