# [C] Network-AI ClaudeHookBridge Deny Pattern Bypass via Truncation

## Summary
Severity: Critical
Advisory: CVE-2026-73614
Aliases: GHSA-743h-jr5x-mpcr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73614
Type: osv

## Details
Network-AI ClaudeHookBridge before 5.15.1 truncates the target string to 500 characters before evaluating denyPatterns, while Claude Code executes the full untruncated command. Attackers can position dangerous content past byte 500 in a Bash command field to bypass the operator's hard-deny list and execute arbitrary commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73614.json
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-743h-jr5x-mpcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-73614
- https://www.vulncheck.com/advisories/network-ai-claudehookbridge-deny-pattern-bypass-via-truncation
