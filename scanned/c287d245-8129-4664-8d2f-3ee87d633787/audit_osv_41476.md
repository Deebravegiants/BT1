# [C] PraisonAI before 4.6.78 Arbitrary File Write and Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-61445
Aliases: GHSA-9mp3-24cc-77mg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-61445
Type: osv

## Details
PraisonAI before 4.6.78 contains arbitrary file write and command execution vulnerabilities in the AICoder component due to missing path validation and command sanitization in LLM tool calls. Attackers can inject malicious prompts through the chat interface to write files to arbitrary filesystem locations and execute arbitrary shell commands with root privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61445.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9mp3-24cc-77mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-61445
- https://www.vulncheck.com/advisories/praisonai-before-arbitrary-file-write-and-command-execution
