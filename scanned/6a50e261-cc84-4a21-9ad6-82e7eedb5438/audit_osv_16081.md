# [M] CVE-2019-25574

## Summary
Severity: Medium
Advisory: CVE-2019-25574
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-03-21
Source: https://osv.dev/vulnerability/CVE-2019-25574
Type: osv

## Details
Green CMS 2.x contains a path traversal vulnerability that allows authenticated attackers to download arbitrary files and directories by injecting directory traversal sequences. Attackers can manipulate the theme_name parameter in the themeexporthandle action or supply base64-encoded file paths to the downfile action to retrieve sensitive files outside intended directories.

## References
- http://www.greencms.net/
- https://codeload.github.com/GreenCMS/GreenCMS/zip/beta
- https://www.vulncheck.com/advisories/green-cms-2-x-path-traversal-arbitrary-file-download
- https://www.exploit-db.com/exploits/46245
