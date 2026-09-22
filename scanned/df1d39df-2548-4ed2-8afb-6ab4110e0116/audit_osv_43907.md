# [C] CodeWhale before 0.8.64 Privilege Escalation via exec_shell_interact

## Summary
Severity: Critical
Advisory: CVE-2026-75857
Aliases: GHSA-g29h-pfmp-qp9r
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75857
Type: osv

## Details
CodeWhale versions >= 0.8.41 and < 0.8.64 contain a vulnerability in the exec_shell_interact (alias exec_interact) tool, whose approval_requirement returns ApprovalRequirement::Auto. This overrides the default Required approval for code-executing tools, so LLM-controlled stdin is written into an already-approved long-running interactive shell (e.g., a python3 -i REPL, mysql, ssh, or sudo -i session) without any approval prompt. An attacker who can inject instructions via untrusted content the agent ingests (a fetched page, MCP result, or repo file) can cause commands to run at the privilege level of that approved process. Fixed in 0.8.64.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75857.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-g29h-pfmp-qp9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-75857
- https://www.vulncheck.com/advisories/codewhale-before-privilege-escalation-via-exec-shell-interact
- https://github.com/Hmbown/CodeWhale/commit/57f3c89471e27ac4032d9791f6885e5d4408c381
