# [H] CraftOS-PC 2's improperly sanitizied paths cause filesystem escape (Windows)

## Summary
Severity: High
Advisory: CVE-2024-43395
Aliases: GHSA-hr3w-wc83-6923
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2024-08-16
Source: https://osv.dev/vulnerability/CVE-2024-43395
Type: osv

## Details
CraftOS-PC 2 is a rewrite of the desktop port of CraftOS from the popular Minecraft mod ComputerCraft using C++ and a modified version of PUC Lua, as well as SDL for drawing. Prior to version 2.8.3, users of CraftOS-PC 2 on Windows can escape the computer folder and access files anywhere without permission or notice by obfuscating `..`s to bypass the internal check preventing parent directory traversal. Version 2.8.3 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43395.json
- https://github.com/MCJack123/craftos2/security/advisories/GHSA-hr3w-wc83-6923
- https://nvd.nist.gov/vuln/detail/CVE-2024-43395
- https://github.com/MCJack123/craftos2/commit/f7a88b905560df4366fb69f09b70f05984e05ad3
