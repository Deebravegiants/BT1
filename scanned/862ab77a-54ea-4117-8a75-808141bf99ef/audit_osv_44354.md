# [M] openssl_encrypt before 1.4.9 Denial of Service via KDF

## Summary
Severity: Medium
Advisory: CVE-2026-81687
Aliases: GHSA-rv6w-7hq9-pr74
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81687
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to enforce a time ceiling on key derivation function iteration counts specified in file metadata. Attackers can craft files with extremely high KDF iteration counts to consume CPU resources for unbounded periods before password verification occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81687.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-rv6w-7hq9-pr74
- https://nvd.nist.gov/vuln/detail/CVE-2026-81687
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-denial-of-service-via-kdf
