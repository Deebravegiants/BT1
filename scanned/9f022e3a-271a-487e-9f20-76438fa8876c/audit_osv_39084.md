# [H] CVE-2026-43823

## Summary
Severity: High
Advisory: CVE-2026-43823
Aliases: GHSA-8q93-f6xh-4f6f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-43823
Type: osv

## Details
When initializing an RSA public key from DER or PEM bytes throws an error, the EVP_PKEY* is double-freed: first in the catch block, then in the deinit. This can lead to a crash on future memory allocations. This double-free manifests when BoringSSL cannot decode the public key from the bytes provided. This vulnerability is addressed in swift-crypto version 4.5.1.

## References
- https://github.com/apple/swift-crypto/security/advisories/GHSA-8q93-f6xh-4f6f
