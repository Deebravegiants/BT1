# [M] PraisonAI before 4.6.78 Prompt Injection Defense Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-61439
Aliases: GHSA-fj8f-m44g-c479
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-61439
Type: osv

## Details
PraisonAI versions before 4.6.78 contain a prompt injection defense misconfiguration where the block threshold defaults to CRITICAL severity, allowing HIGH-level threats to pass through unblocked. Attackers can submit single-vector prompt injection attacks such as instruction overrides or financial manipulation that trigger HIGH severity detection but are logged without blocking, enabling system prompt extraction and unauthorized tool invocations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61439.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-fj8f-m44g-c479
- https://nvd.nist.gov/vuln/detail/CVE-2026-61439
- https://www.vulncheck.com/advisories/praisonai-before-prompt-injection-defense-bypass
