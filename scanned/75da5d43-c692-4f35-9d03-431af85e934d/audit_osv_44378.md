# [M] openssl_encrypt before 1.4.9 Weak Cryptographic Parameters

## Summary
Severity: Medium
Advisory: CVE-2026-81718
Aliases: GHSA-fmjx-p826-6fvr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81718
Type: osv

## Details
openssl_encrypt versions before 1.4.9 use under-parameterized PBKDF2-HMAC-SHA256 with only 100,000 iterations to protect PQC keyfile private keys and 10,000 iterations for dual-encryption file-password verification. Attackers who obtain keyfiles or encrypted files can brute-force wrapping passwords offline using GPU or ASIC acceleration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81718.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-fmjx-p826-6fvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-81718
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-weak-cryptographic-parameters
