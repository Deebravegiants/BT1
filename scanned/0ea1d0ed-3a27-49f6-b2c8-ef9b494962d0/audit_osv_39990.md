# [H] Notepad++: Arbitrary Code Execution via shortcuts.xml UserCommand Injection

## Summary
Severity: High
Advisory: CVE-2026-48800
Aliases: GHSA-3x3f-3j39-pj3v
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-48800
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.6.1, the <Command> tag text content inside <UserDefinedCommands> in shortcuts.xml is read by NppXml::value(aNode) (Parameters.cpp:3658) in the feedUserCmds() function and stored in UserCommand._cmd without any validation. When the user clicks the corresponding entry in the Run menu, NppCommands.cpp:4264 creates a Command object with string2wstring(ucmd.getCmd()) and calls run(), which invokes ShellExecute (RunDlg.cpp:221) with the attacker-controlled string as the executable path. The injected command appears as a normal menu item in the Run menu, making it a viable persistence mechanism.  This vulnerability is fixed in 8.9.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48800.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-3x3f-3j39-pj3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-48800
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/6b3dc52a9245c6d8c6287a8d6d93a30981c05feb
