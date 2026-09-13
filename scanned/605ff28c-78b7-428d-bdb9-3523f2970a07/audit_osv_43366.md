# [H] Flowise before 3.1.3 Sandbox Escape via Pandas Methods

## Summary
Severity: High
Advisory: CVE-2026-73484
Aliases: GHSA-x58f-9m57-qc4m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73484
Type: osv

## Details
Flowise before 3.1.3 contains a sandbox escape vulnerability in pythonCodeValidator.ts that fails to block native Pandas DataFrame methods like to_csv, to_json, pipe, and query. Authenticated attackers can exploit this to exfiltrate uploaded CSV data or write arbitrary files to the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73484.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x58f-9m57-qc4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-73484
- https://www.vulncheck.com/advisories/flowise-before-sandbox-escape-via-pandas-methods
