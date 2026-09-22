# [H] Git GUI malicious command injection on Windows

## Summary
Severity: High
Advisory: CVE-2025-46334
Aliases: GHSA-7px4-9hg2-fvhx
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-46334
Type: osv

## Details
Git GUI allows you to use the Git source control management tools via a GUI. A malicious repository can ship versions of sh.exe or typical textconv filter programs such as astextplain. Due to the unfortunate design of Tcl on Windows, the search path when looking for an executable always includes the current directory. The mentioned programs are invoked when the user selects Git Bash or Browse Files from the menu. This vulnerability is fixed in 2.43.7, 2.44.4, 2.45.4, 2.46.4, 2.47.3, 2.48.2, 2.49.1, and 2.50.1.

## References
- http://www.openwall.com/lists/oss-security/2025/07/08/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46334.json
- https://github.com/j6t/git-gui/compare/dcda716dbc9c90bcac4611bd1076747671ee0906..a1ccd2512072cf52835050f4c97a4fba9f0ec8f9
- https://github.com/j6t/git-gui/security/advisories/GHSA-7px4-9hg2-fvhx
- https://nvd.nist.gov/vuln/detail/CVE-2025-46334
