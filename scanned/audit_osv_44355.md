# [M] openssl_encrypt before 1.4.9 Plaintext Confirmation Oracle via SHA-256

## Summary
Severity: Medium
Advisory: CVE-2026-81688
Aliases: GHSA-7c3q-gp4v-q29q, PYSEC-2026-3795
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81688
Type: osv

## Details
openssl_encrypt versions before 1.4.9 store an unkeyed SHA-256 hash of the plaintext in the cleartext file header metadata. Attackers can read this hash without the password to confirm guessed plaintexts offline or fingerprint identical plaintexts across separately-encrypted files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81688.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-7c3q-gp4v-q29q
- https://nvd.nist.gov/vuln/detail/CVE-2026-81688
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-plaintext-confirmation-oracle-via-sha-256
