# [M] CVE-2021-47749

## Summary
Severity: Medium
Advisory: CVE-2021-47749
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2021-47749
Type: osv

## Details
YouPHPTube <= 7.8 contains a local file inclusion vulnerability that allows unauthenticated attackers to access arbitrary files by manipulating the 'lang' parameter in GET requests. Attackers can exploit the path traversal flaw in locale/function.php to include and view PHP files outside the intended directory by using directory traversal sequences.

## References
- https://web.archive.org/web/20170506141644/https://www.youphptube.com/
- https://www.vulncheck.com/advisories/youphptube-directory-traversal
- https://www.exploit-db.com/exploits/51101
