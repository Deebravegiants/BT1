# [M] AgentScope Vulnerable to Remote Code Injection

## Summary
Severity: Medium
Advisory: GHSA-cr24-fv3h-8cjm
CVE: CVE-2026-6603
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-cr24-fv3h-8cjm
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A vulnerability was determined in modelscope agentscope up to 1.0.18. Affected by this vulnerability is the function execute_python_code/execute_shell_command of the file src/AgentScope/tool/_coding/_python.py. This manipulation causes code injection. The attack is possible to be carried out remotely. The exploit has been publicly disclosed and may be utilized. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6603
- https://gist.github.com/YLChen-007/c084d69aaeda6729f3988603f2b0ce6e
- https://github.com/agentscope-ai/agentscope
- https://vuldb.com/submit/792223
- https://vuldb.com/vuln/358238
- https://vuldb.com/vuln/358238/cti
