# [M] openssl_encrypt before 1.4.9 Weak Key Derivation via D-Bus

## Summary
Severity: Medium
Advisory: CVE-2026-81704
Aliases: GHSA-v9r6-grch-fxw7, PYSEC-2026-3963
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81704
Type: osv

## Details
openssl_encrypt versions before 1.4.9 contain a weak key derivation vulnerability in the D-Bus CryptoService.EncryptFile handler that uses unstretched SHA-256 instead of Argon2id. Attackers can perform offline password guessing against encrypted files roughly six to seven orders of magnitude faster than documented protection by exploiting the missing key stretching and hash rounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81704.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-v9r6-grch-fxw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-81704
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-weak-key-derivation-via-d-bus
