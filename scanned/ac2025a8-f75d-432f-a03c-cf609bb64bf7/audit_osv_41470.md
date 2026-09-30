# [C] PraisonAI before 4.6.78 Remote Code Execution via Broken AST Sandbox

## Summary
Severity: Critical
Advisory: CVE-2026-61438
Aliases: GHSA-26mh-57q7-jfvr
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61438
Type: osv

## Details
PraisonAI before 4.6.78 contains a remote code execution vulnerability in JobWorkflowExecutor._exec_inline_python() due to insufficient AST validation of workflow script steps. Attackers can create malicious YAML workflow files with import os statements followed by os.system() calls that bypass sandbox checks and execute arbitrary OS commands with process privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61438.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-26mh-57q7-jfvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-61438
- https://www.vulncheck.com/advisories/praisonai-before-remote-code-execution-via-broken-ast-sandbox
