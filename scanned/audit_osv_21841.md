# [M] CVE-2021-47872

## Summary
Severity: Medium
Advisory: CVE-2021-47872
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2021-47872
Type: osv

## Details
SEO Panel versions prior to 4.9.0 contain a blind SQL injection vulnerability in the archive.php page that allows authenticated attackers to manipulate database queries through the 'order_col' parameter. Attackers can use sqlmap to exploit the vulnerability and extract database information by injecting malicious SQL code into the order column parameter.

## References
- https://github.com/seopanel/Seo-Panel/releases/tag/4.9.0
- https://www.exploit-db.com/exploits/49666
- https://www.seopanel.org/
- https://www.vulncheck.com/advisories/seo-panel-ordercol-blind-sql-injection
- https://github.com/seopanel/Seo-Panel/issues/209
