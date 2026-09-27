# [H] BleachBit for Windows Has DLL Untrusted Path Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-32780
Aliases: GHSA-ghph-v4x4-vr3c
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32780
Type: osv

## Details
BleachBit cleans files to free disk space and to maintain privacy. BleachBit for Windows up to version 4.6.2 is vulnerable to a DLL Hijacking vulnerability. By placing a malicious DLL with the name uuid.dll in the folder C:\Users\<username>\AppData\Local\Microsoft\WindowsApps\, an attacker can execute arbitrary code every time BleachBit is run. This issue has been patched in version 4.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32780.json
- https://github.com/bleachbit/bleachbit/security/advisories/GHSA-ghph-v4x4-vr3c
- https://nvd.nist.gov/vuln/detail/CVE-2025-32780
- https://github.com/bleachbit/bleachbit/commit/dafeba57dcb14c7ec4a97224ff1408f6b0c2a7f8
