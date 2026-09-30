# [H] pyLoad: Arbitrary File Deletion via Path Traversal during Encrypted 7z Password Verification

## Summary
Severity: High
Advisory: CVE-2026-32808
Aliases: GHSA-7g4m-8hx2-4qh3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32808
Type: osv

## Details
pyLoad is a free and open-source download manager written in Python. Versions before 0.5.0b3.dev97 are vulnerable to path traversal during password verification of certain encrypted 7z archives (encrypted files with non-encrypted headers), causing arbitrary file deletion outside of the extraction directory. During password verification, pyLoad derives an archive entry name from 7z listing output and treats it as a filesystem path without constraining it to the extraction directory. This issue has been fixed in version 0.5.0b3.dev97.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32808.json
- https://github.com/pyload/pyload/security/advisories/GHSA-7g4m-8hx2-4qh3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32808
