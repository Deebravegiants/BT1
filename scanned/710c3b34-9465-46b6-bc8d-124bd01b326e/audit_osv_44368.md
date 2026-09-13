# [C] openssl_encrypt before 1.4.9 Key Substitution via Identity Load

## Summary
Severity: Critical
Advisory: CVE-2026-81702
Aliases: GHSA-q8p3-7h6h-ghfr, PYSEC-2026-3962
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81702
Type: osv

## Details
openssl_encrypt before 1.4.9 fails to re-derive and validate fingerprints when loading identities from identity.json, allowing attackers to substitute public keys in identity stores. Attackers can replace legitimate public keys with their own while maintaining the claimed fingerprint, enabling silent key substitution where encryption uses attacker keys and signature verification appears valid.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81702.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-q8p3-7h6h-ghfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-81702
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-key-substitution-via-identity-load
