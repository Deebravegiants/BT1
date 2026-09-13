# [H] Notepad++: Path Traversal (Zip Slip) in WinGup Plugin Extraction

## Summary
Severity: High
Advisory: CVE-2026-57233
Aliases: GHSA-hjxw-84rf-wg5r
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-57233
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.7, the WinGup decompress function joins untrusted ZIP entry names to unzipDestTo without canonical containment validation, allowing an entry such as ../mimeTools/mimeTools.dll to overwrite a DLL in a sibling plugin directory and execute attacker-controlled code when Notepad++ next loads that plugin. This issue is fixed in version 8.9.7.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57233.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-hjxw-84rf-wg5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-57233
- https://github.com/notepad-plus-plus/wingup/commit/7670296a5c7fdec624e0a45dbde51059a7d735a8
- https://github.com/notepad-plus-plus/wingup/pull/106
