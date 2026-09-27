# [M] agentverus-scanner Companion Code Analysis Bypass via Excluded Python Bytecode

## Summary
Severity: Medium
Advisory: CVE-2026-84811
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84811
Type: osv

## Details
agentverus-scanner fails to analyze compiled Python bytecode files in companion code directories, allowing attackers to bypass security scanning by shipping malicious __pycache__ entries alongside benign source files. Attackers can execute arbitrary Python bytecode on import while the scanner reports a CERTIFIED verdict with high trust scores in both static and semantic analysis modes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84811.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84811
- https://www.vulncheck.com/advisories/agentverus-scanner-companion-code-analysis-bypass-via-excluded-python-bytecode
- https://github.com/agentverus/agentverus-scanner/issues/27
- https://github.com/agentverus/agentverus-scanner
- https://github.com/agentverus/agentverus-scanner/blob/v0.8.1/src/scanner/analyzers/semantic.ts
- https://github.com/agentverus/agentverus-scanner/blob/v0.8.1/src/scanner/companion-code.ts
