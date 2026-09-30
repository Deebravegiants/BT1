# [C] Flowise before 3.1.3 Code Injection via CSV Agent customReadCSV

## Summary
Severity: Critical
Advisory: CVE-2026-73486
Aliases: GHSA-4878-cqgq-j53v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73486
Type: osv

## Details
Flowise before 3.1.3 contains a code injection vulnerability in the CSV Agent node's customReadCSV parameter that allows authenticated attackers to execute arbitrary Python code. The validator uses a static regex blocklist that can be bypassed through obfuscation techniques, enabling attackers to execute code in the unsandboxed pyodide environment with full system access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73486.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-4878-cqgq-j53v
- https://nvd.nist.gov/vuln/detail/CVE-2026-73486
- https://www.vulncheck.com/advisories/flowise-before-code-injection-via-csv-agent-customreadcsv
