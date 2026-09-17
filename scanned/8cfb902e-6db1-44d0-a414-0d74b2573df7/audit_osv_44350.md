# [C] openssl_encrypt before 1.4.9 Plaintext Private Key Storage

## Summary
Severity: Critical
Advisory: CVE-2026-81683
Aliases: GHSA-r8gw-6hfj-98jw, PYSEC-2026-3792
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81683
Type: osv

## Details
openssl_encrypt (pip package openssl-encrypt) versions 1.4.8 and earlier store an mTLS client private key in cleartext within a world-readable (0644) SharedPreferences file via the desktop GUI's Settings screen 'combined certificate and private key' PEM field. A local attacker with file system access can read the exposed private key. Version 1.4.9 writes the PEM to a dedicated 0600 file, keeps only its path in SharedPreferences, and migrates/scrubs existing cleartext values.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81683.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-r8gw-6hfj-98jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-81683
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-plaintext-private-key-storage
