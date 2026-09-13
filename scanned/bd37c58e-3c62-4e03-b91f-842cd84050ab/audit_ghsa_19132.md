# [C] PandasAI interactive prompt function Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-vv2h-2w3q-3fx7
CVE: CVE-2024-12366
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-vv2h-2w3q-3fx7
Type: github-advisory

## Affected
- PyPI: `pandasai` — affected >=0

## Details
PandasAI uses an interactive prompt function that is vulnerable to prompt injection and run arbitrary Python code that can lead to Remote Code Execution (RCE) instead of the intended explanation of the natural language processing by the LLM. The security controls of PandasAI (2.4.3 and earlier) fail to distinguish between legitimate and malicious inputs, allowing the attackers to manipulate the system into executing untrusted code, leading to untrusted code execution (RCE), system compromise, or pivoting attacks on connected services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12366
- https://docs.getpanda.ai/v3/privacy-security
- https://docs.pandas-ai.com/advanced-security-agent
- https://github.com/sinaptik-ai/pandas-ai
- https://www.kb.cert.org/vuls/id/148244
