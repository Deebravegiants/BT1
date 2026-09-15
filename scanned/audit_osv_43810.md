# [M] openssl_encrypt before 1.4.6 KDF Bypass via Sequential-XOR

## Summary
Severity: Medium
Advisory: CVE-2026-74871
Aliases: GHSA-vxf9-vwp6-2w43, PYSEC-2026-3976
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74871
Type: osv

## Details
openssl_encrypt versions before 1.4.6 contain a key derivation flaw in sequential XOR composition mode where the last stage cancels out during key generation. When configured with a single KDF and no prior hashing stage, attackers can bypass memory-hard key derivation and perform offline password cracking at SHA-256 speed instead of the configured KDF cost.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74871.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-vxf9-vwp6-2w43
- https://nvd.nist.gov/vuln/detail/CVE-2026-74871
- https://www.vulncheck.com/advisories/openssl-encrypt-before-kdf-bypass-via-sequential-xor
