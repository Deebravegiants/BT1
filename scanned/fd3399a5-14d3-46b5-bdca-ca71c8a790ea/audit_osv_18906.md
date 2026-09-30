# [M] CVE-2020-37214

## Summary
Severity: Medium
Advisory: CVE-2020-37214
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2020-37214
Type: osv

## Details
Voyager 1.3.0 contains a directory traversal vulnerability that allows attackers to access sensitive system files by manipulating the asset path parameter. Attackers can exploit the path parameter in /admin/voyager-assets to read arbitrary files like /etc/passwd and .env configuration files.

## References
- https://github.com/the-control-group/voyager/releases/tag/v1.2.7
- https://github.com/the-control-group/voyager/releases/tag/v1.3.0
- https://voyager.devdojo.com/
- https://www.exploit-db.com/exploits/47875
- https://www.vulncheck.com/advisories/voyager-directory-traversal
