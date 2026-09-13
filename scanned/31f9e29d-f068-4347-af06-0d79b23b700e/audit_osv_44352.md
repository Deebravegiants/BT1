# [C] openssl_encrypt before 1.4.9 Text Injection via Recovery Slot Metadata

## Summary
Severity: Critical
Advisory: CVE-2026-81685
Aliases: GHSA-49h2-qmcq-wvvc, PYSEC-2026-3793
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81685
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to sanitize recovery-slot metadata in the desktop GUI, allowing attackers to inject control characters and line separators into the irreversible-removal confirmation dialog. Attackers can craft encrypted files with malicious slot identifiers containing bidi overrides or line-separator characters to forge warning text and deceive users during file removal operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81685.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-49h2-qmcq-wvvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-81685
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-text-injection-via-recovery-slot-metadata
