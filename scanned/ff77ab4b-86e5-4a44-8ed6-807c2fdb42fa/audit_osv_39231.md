# [C] HRConvert2: Missing Sanitization enables Unauthenticated Remote Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-44666
Aliases: GHSA-f74g-4wj8-j35h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44666
Type: osv

## Details
HRConvert2 is a self-hosted, drag-and-drop & nosql file conversion server & share tool. Prior to 3.3.8, the sanitizeString() function in convertCore.php is missing backtick (`) and tab (\t) from its strip list. User input then reaches shell_exec(), where the shell interprets these characters and commands within filenames execute. This vulnerability is fixed in 3.3.8.

## References
- https://github.com/zelon88/HRConvert2/releases/tag/v3.3.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44666.json
- https://github.com/zelon88/HRConvert2/security/advisories/GHSA-f74g-4wj8-j35h
- https://nvd.nist.gov/vuln/detail/CVE-2026-44666
