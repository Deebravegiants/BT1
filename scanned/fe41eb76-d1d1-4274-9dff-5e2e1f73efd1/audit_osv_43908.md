# [C] CodeWhale rlm_eval before 0.8.64 Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-75858
Aliases: GHSA-wrj3-vj8c-784f
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75858
Type: osv

## Details
CodeWhale (packages codewhale / codewhale-tui) versions >= 0.8.41 and < 0.8.64 contain a remote code execution vulnerability in the rlm_eval tool. The tool's approval_requirement() returns ApprovalRequirement::Auto, which the engine treats as 'never prompt,' causing arbitrary model-supplied Python code to run in a python3 interpreter without consulting the user's configured --approval-policy and without any approval prompt or audit step. An attacker can induce the agent to execute arbitrary code via prompt injection in untrusted content the agent reads (a web page, fetched URL, repository file, or MCP tool result); the companion rlm_open tool can stage such content. Code runs on the user's machine at the user's privilege level. Fixed in 0.8.64.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75858.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-wrj3-vj8c-784f
- https://nvd.nist.gov/vuln/detail/CVE-2026-75858
- https://www.vulncheck.com/advisories/codewhale-rlm-eval-before-remote-code-execution
- https://github.com/Hmbown/CodeWhale/commit/57f3c89471e27ac4032d9791f6885e5d4408c381
