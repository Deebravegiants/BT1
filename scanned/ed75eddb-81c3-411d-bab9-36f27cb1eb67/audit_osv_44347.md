# [C] openssl_encrypt before 1.4.9 Authentication Bypass via Recovery Slot Removal

## Summary
Severity: Critical
Advisory: CVE-2026-81680
Aliases: GHSA-grhj-cpmg-f5mx, PYSEC-2026-3957
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81680
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to authenticate recovery-slot presence in envelope-format encrypted files, allowing attackers to remove recovery slots without re-encrypting the payload. Attackers can modify the file header to delete recovery-slot fields and bypass authentication, silently removing recovery paths the owner deliberately added.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81680.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-grhj-cpmg-f5mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-81680
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-authentication-bypass-via-recovery-slot-removal
