# [H] Buffer overflow in deserialization in oqs-provider

## Summary
Severity: High
Advisory: CVE-2024-37305
Aliases: GHSA-pqvr-5cr8-v6fx
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-06-17
Source: https://osv.dev/vulnerability/CVE-2024-37305
Type: osv

## Details
oqs-provider is a provider for the OpenSSL 3 cryptography library that adds support for post-quantum cryptography in TLS, X.509, and S/MIME using post-quantum algorithms from liboqs. Flaws have been identified in the way oqs-provider handles lengths decoded with DECODE_UINT32 at the start of serialized hybrid (traditional + post-quantum) keys and signatures. Unchecked length values are later used for memory reads and writes; malformed input can lead to crashes or information leakage. Handling of plain/non-hybrid PQ key operation is not affected. This issue has been patched in in v0.6.1. All users are advised to upgrade. There are no workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37305.json
- https://github.com/open-quantum-safe/oqs-provider/security/advisories/GHSA-pqvr-5cr8-v6fx
- https://nvd.nist.gov/vuln/detail/CVE-2024-37305
- https://github.com/open-quantum-safe/oqs-provider/pull/416
