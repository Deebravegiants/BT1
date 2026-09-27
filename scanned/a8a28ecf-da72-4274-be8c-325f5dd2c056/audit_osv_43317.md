# [C] Notepad++: Install-time PowerShell command injection through installation path

## Summary
Severity: Critical
Advisory: CVE-2026-73250
Aliases: GHSA-gp2r-262h-9hgf
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73250
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.7, the Notepad++ Windows 11 x64 and ARM64 installer passes the attacker-influenced installation directory `$INSTDIR` from PowerEditor/installer/nppSetup.nsi into a PowerShell `-Command` string used by RegisterMSIX to invoke Add-AppxPackage, allowing PowerShell subexpression syntax such as `$()` in the installation path to execute commands in the installer's security context when the context menu component is selected. This issue is fixed in version 8.9.7.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73250.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-gp2r-262h-9hgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-73250
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/3764d5b72664ef95421bc53bcb204f9b977d346b
