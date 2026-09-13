# [C] Notepad++: shortcuts.xml Macro HMAC Bypass Enables Conditional Elevated Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-71858
Aliases: GHSA-f4rj-vqq4-wvg4
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71858
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.7, macros loaded from an attacker-controlled shortcuts.xml bypass the HMAC validation applied to UserDefinedCommands and can invoke Scintilla actions and the internal Open in Default Viewer command in an elevated Notepad++ process, allowing protected file modification and conditional elevated command execution when a local attacker influences settingsDir and a user triggers the macro. This issue is fixed in version 8.9.7.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71858.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-f4rj-vqq4-wvg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-71858
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/7686e5a3025eaf1fb8e024c2ceb54670ea05f5fb
