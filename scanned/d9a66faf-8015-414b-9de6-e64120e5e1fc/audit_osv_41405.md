# [M] PraisonAI before 4.6.78 Unenforced Security Policy in Subprocess Sandbox

## Summary
Severity: Medium
Advisory: CVE-2026-60085
Aliases: GHSA-5r6c-gj4g-r697
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-60085
Type: osv

## Details
PraisonAI before 4.6.78 contains an unenforced security policy vulnerability in the default Subprocess Sandbox backend where blocked_commands, blocked_paths, blocked_imports, allow_subprocess, and allow_file_write restrictions are completely ignored. Attackers can execute arbitrary subprocess commands, read sensitive files, and perform destructive operations despite explicit security policy configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60085.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5r6c-gj4g-r697
- https://nvd.nist.gov/vuln/detail/CVE-2026-60085
- https://www.vulncheck.com/advisories/praisonai-before-unenforced-security-policy-in-subprocess-sandbox
