# [C] openssl_encrypt before 1.4.0 Weak Key Derivation via HKDF

## Summary
Severity: Critical
Advisory: CVE-2026-74889
Aliases: GHSA-j9mh-57cc-665x, PYSEC-2026-3765
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74889
Type: osv

## Details
openssl_encrypt versions before 1.4.0 use HKDF with no salt and static info parameter in key normalization functions, reducing entropy extraction and determinism. Attackers can exploit predictable key derivation with identical inputs to weaken cryptographic security against multi-target attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74889.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-j9mh-57cc-665x
- https://nvd.nist.gov/vuln/detail/CVE-2026-74889
- https://www.vulncheck.com/advisories/openssl-encrypt-before-weak-key-derivation-via-hkdf
