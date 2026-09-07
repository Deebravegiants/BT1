# [H] WiX Toolset's .be TEMP folder is vulnerable to DLL redirection attacks that allow the attacker to escalate privileges

## Summary
Severity: High
Advisory: GHSA-7wh2-wxc7-9ph5
CVE: CVE-2024-24810
CWE: CWE-426
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-7wh2-wxc7-9ph5
Type: github-advisory

## Affected
- NuGet: `wix` — affected >=4.0.0 <4.0.4
- NuGet: `wix` — affected >=0 <3.14.0

## Details
### Summary
.be TEMP folder is vulnerable to DLL redirection attacks that allow the attacker to escalate privileges.

### Details
If the bundle is not run as admin, the user's TEMP folder is used and not the system TEMP folder. A utility is able to monitor the user's TEMP folder for changes and drop its own DLL into the **.be/<bundle>.Local** folder immediately when the .be folder is created. When the burn engine elevates, the malicious DLL receives elevated privileges.

### PoC
As a standard, non-admin user:
1. Monitor the user's TEMP folder for changes using ReadDirectoryChangesW
2. On FILE_ACTION_ADDED, check if the folder name is .be
3. Create a folder in .be named after the bundle + .Local (e.g. MyInstaller.exe.Local)
4. Put the malicious COMCTL32.DLL in the .Local folder following the naming used for the real DLL (e.g. MyInstaller.exe.Local/x86_microsoft.windows.common-controls_.../COMCTL32.dll)
5. Do hacker things when the engine escalates and the malicious DLL is loaded

Proper naming for the path can be obtained by using GetModuleHandle("comctl32.dll") and GetModuleFileName.

### Impact
DLL redirection utilizing .exe.Local Windows capability. This impacts any installer built with the WiX installer framework.

## References
- https://github.com/wixtoolset/issues/security/advisories/GHSA-7wh2-wxc7-9ph5
- https://nvd.nist.gov/vuln/detail/CVE-2024-24810
- https://github.com/wixtoolset/wix/commit/fec38b6461d0551339139a2fe52403a61942adc0
- https://github.com/wixtoolset/wix
