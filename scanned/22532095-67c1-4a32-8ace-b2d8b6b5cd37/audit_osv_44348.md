# [C] openssl_encrypt before 1.4.9 False Encryption via Cleartext Storage

## Summary
Severity: Critical
Advisory: CVE-2026-81681
Aliases: GHSA-2jv6-qqfm-m46m, PYSEC-2026-3791
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81681
Type: osv

## Details
openssl_encrypt (pip package openssl-encrypt) versions <= 1.4.8 advertise a portable USB workspace as an 'Encrypted USB Workspace' with AES-256-GCM encryption and write a marker declaring the workspace encrypted, but the workspace directory is actually stored in cleartext and the derived encryption key is never applied to it. A user who trusts the branding and places files in the workspace leaves them unencrypted on the removable media, so an attacker with physical access to the media can read the sensitive files. Fixed in 1.4.9, which seals the workspace into an authenticated AES-256-GCM vault.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81681.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-2jv6-qqfm-m46m
- https://nvd.nist.gov/vuln/detail/CVE-2026-81681
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-false-encryption-via-cleartext-storage
