# [H] cryptography NULL pointer dereference with pkcs12.serialize_key_and_certificates when called with a non-matching certificate and private key and an hmac_hash override

## Summary
Severity: High
Advisory: GHSA-6vqw-3v5j-54x4
CVE: CVE-2024-26130
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-6vqw-3v5j-54x4
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=38.0.0 <42.0.4

## Details
If `pkcs12.serialize_key_and_certificates` is called with both:

1. A certificate whose public key did not match the provided private key
2. An `encryption_algorithm` with `hmac_hash` set (via `PrivateFormat.PKCS12.encryption_builder().hmac_hash(...)`

Then a NULL pointer dereference would occur, crashing the Python process.

This has been resolved, and now a `ValueError` is properly raised.

Patched in https://github.com/pyca/cryptography/pull/10423

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-6vqw-3v5j-54x4
- https://nvd.nist.gov/vuln/detail/CVE-2024-26130
- https://github.com/pyca/cryptography/pull/10423
- https://github.com/pyca/cryptography/commit/97d231672763cdb5959a3b191e692a362f1b9e55
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2024-225.yaml
