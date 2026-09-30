# [M] Notepad++: session.xml backupFilePath starts_with Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-52886
Aliases: GHSA-rqfm-pw34-r7j6
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-52886
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.7, Notepad++ validates the backupFilePath attribute from session.xml with std::wstring::starts_with against the expected backup directory without path normalization, allowing parent-directory sequences during snapshot-mode restoration to read an arbitrary user-readable file outside the backup directory into an editor tab. This issue is fixed in version 8.9.7.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52886.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-rqfm-pw34-r7j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-52886
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/7e66f36db666a13b09fb5c31232ab2ca1c2ebccc
