# [M] openssl_encrypt before 1.4.9 Authentication Bypass via Unencrypted PQC Key

## Summary
Severity: Medium
Advisory: CVE-2026-81703
Aliases: GHSA-qqfq-g2cv-j7v3, PYSEC-2026-3779
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81703
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to validate encryption status of embedded post-quantum private keys in file metadata. Attackers can craft files with unencrypted embedded PQC keys that decrypt under any password, bypassing authentication and producing attacker-chosen plaintext with false integrity verification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81703.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-qqfq-g2cv-j7v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-81703
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-authentication-bypass-via-unencrypted-pqc-key
