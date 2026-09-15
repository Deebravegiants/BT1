# [H] DLL Search Order Hijacking vulnerability in BleachBit for Windows

## Summary
Severity: High
Advisory: CVE-2023-47113
Aliases: GHSA-j8jc-f6p7-55p8
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-08
Source: https://osv.dev/vulnerability/CVE-2023-47113
Type: osv

## Details
BleachBit cleans files to free disk space and to maintain privacy. BleachBit for Windows up to version 4.4.2 is vulnerable to a DLL Hijacking vulnerability. By placing a DLL in the Folder c:\DLLs, an attacker can run arbitrary code on every execution of BleachBit for Windows. This issue has been patched in version 4.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47113.json
- https://github.com/bleachbit/bleachbit/security/advisories/GHSA-j8jc-f6p7-55p8
- https://nvd.nist.gov/vuln/detail/CVE-2023-47113
