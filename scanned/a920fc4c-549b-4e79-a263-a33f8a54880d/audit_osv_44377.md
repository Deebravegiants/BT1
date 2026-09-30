# [C] openssl_encrypt before 1.4.9 Integrity Bypass via Added Files

## Summary
Severity: Critical
Advisory: CVE-2026-81717
Aliases: GHSA-8jx3-27qf-3p97, PYSEC-2026-3801
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81717
Type: osv

## Details
openssl_encrypt (pip package openssl-encrypt) before 1.4.9 contains two weaknesses in the portable USB drive feature, whose threat model treats the removable drive as untrusted (attacker with physical write access). USBDriveCreator._verify_integrity_file only validates files listed in the manifest, so files added to the drive — including a root-level autorun payload — are not detected and integrity verification still passes. Additionally, a globally constant, source-embedded KDF salt (_LEGACY_FIXED_SALT) is used to derive the drive encryption key for any drive lacking a per-drive salt file, defeating precomputation resistance and enabling an offline rainbow-table attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81717.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-8jx3-27qf-3p97
- https://nvd.nist.gov/vuln/detail/CVE-2026-81717
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-integrity-bypass-via-added-files
