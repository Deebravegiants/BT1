# [H] Notepad++: Arbitrary Code Execution via config.xml commandLineInterpreter

## Summary
Severity: High
Advisory: CVE-2026-48778
Aliases: GHSA-7hm3-wp5q-ccv9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-48778
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.6.1, the <GUIConfig name="commandLineInterpreter"> tag in config.xml is read by NppXml::value() (Parameters.cpp:6430) and stored in _nppGUI._commandLineInterpreter without any validation, whitelist, or digital signature check. When the user triggers IDM_FILE_OPEN_CMD (File → Open Containing Folder → cmd), NppCommands.cpp:228 creates a Command object with this value and calls run(), which invokes ShellExecute (RunDlg.cpp:221) with the attacker-controlled string as the executable path. This vulnerability is fixed in 8.9.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48778.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-7hm3-wp5q-ccv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48778
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/24c7b5c63cece76dbc8c4f2607a27ebfe22fa614
