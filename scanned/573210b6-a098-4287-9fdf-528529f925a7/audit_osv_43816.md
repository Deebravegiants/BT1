# [M] openssl_encrypt before 1.4.0 Non-Standard PBKDF2 Key Derivation

## Summary
Severity: Medium
Advisory: CVE-2026-74888
Aliases: GHSA-743f-89fg-x288, PYSEC-2026-3764
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74888
Type: osv

## Details
openssl_encrypt versions before 1.4.0 use a non-standard PBKDF2 key derivation construction with iterations=1 per call in an outer loop, creating a KDF whose security properties have not been formally analyzed. Attackers can exploit this weakened key derivation to more efficiently crack passwords protecting legacy encrypted files compared to standard PBKDF2 implementations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74888.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-743f-89fg-x288
- https://nvd.nist.gov/vuln/detail/CVE-2026-74888
- https://www.vulncheck.com/advisories/openssl-encrypt-before-non-standard-pbkdf2-key-derivation
