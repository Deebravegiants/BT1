# [C] CVE-2020-37117

## Summary
Severity: Critical
Advisory: CVE-2020-37117
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-05
Source: https://osv.dev/vulnerability/CVE-2020-37117
Type: osv

## Details
jizhiCMS 1.6.7 contains a file download vulnerability in the admin plugins update endpoint that allows authenticated administrators to download arbitrary files. Attackers can exploit the vulnerability by sending crafted POST requests with malicious filepath and download_url parameters to trigger unauthorized file downloads.

## References
- https://www.jizhicms.cn/
- https://www.vulncheck.com/advisories/jizhicms-arbitrary-file-download
- https://www.exploit-db.com/exploits/48361
