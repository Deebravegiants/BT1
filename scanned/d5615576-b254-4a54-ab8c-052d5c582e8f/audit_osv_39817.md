# [C] TypeBot vulnerable to CSV injection in result export

## Summary
Severity: Critical
Advisory: CVE-2026-47705
Aliases: GHSA-p52m-h5qg-8p8w
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-47705
Type: osv

## Details
TypeBot is a chatbot builder tool. Version 3.16.1 has a CSV injection vulnerability in the result export functionality. The application does not sanitize or escape user-supplied input when generating CSV files. An attacker can inject spreadsheet formulas into input fields, which are later executed when an administrator opens the exported CSV in spreadsheet software such as Microsoft Excel or LibreOffice Calc. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47705.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-p52m-h5qg-8p8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-47705
- https://github.com/baptisteArno/typebot.io/commit/89682dd4ad56f33263332fa377beb01ad616c27c
- https://github.com/baptisteArno/typebot.io/pull/2493
