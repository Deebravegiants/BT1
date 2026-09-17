# [M] PraisonAI before 4.6.78 Path Traversal via Custom Commands

## Summary
Severity: Medium
Advisory: CVE-2026-60088
Aliases: GHSA-xpx6-x8c2-mw5w
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-60088
Type: osv

## Details
PraisonAI before 4.6.78 fails to validate file path references in custom command templates, allowing attackers to read files outside the workspace. Attackers can include path traversal sequences like @../outside_secret.txt or absolute paths in project command files to exfiltrate process-readable files into model prompts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60088.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-xpx6-x8c2-mw5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-60088
- https://www.vulncheck.com/advisories/praisonai-before-path-traversal-via-custom-commands
- https://github.com/MervinPraison/PraisonAI/commit/3aa9cbc2bd49c23a32be0a89a5e620d13d843eab
