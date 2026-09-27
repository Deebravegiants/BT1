# [H] CVE-2020-8146

## Summary
Severity: High
Advisory: CVE-2020-8146
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-04-01
Source: https://osv.dev/vulnerability/CVE-2020-8146
Type: osv

## Details
In UniFi Video v3.10.1 (for Windows 7/8/10 x64) there is a Local Privileges Escalation to SYSTEM from arbitrary file deletion and DLL hijack vulnerabilities. The issue was fixed by adjusting the .tsExport folder when the controller is running on Windows and adjusting the SafeDllSearchMode in the windows registry when installing UniFi-Video controller. Affected Products: UniFi Video Controller v3.10.2 (for Windows 7/8/10 x64) and prior. Fixed in UniFi Video Controller v3.10.3 and newer.

## References
- https://community.ui.com/releases/Security-advisory-bulletin-006-006/3cf6264e-e0e6-4e26-a331-1d271f84673e
