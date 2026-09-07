# [H] AgentScope uses `eval`

## Summary
Severity: High
Advisory: GHSA-6p55-qr3j-mpgq
CVE: CVE-2024-48050
CWE: CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-6p55-qr3j-mpgq
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
In agentscope <=v0.0.4, the file `agentscope\web\workstation\workflow_utils.py` has the function `is_callable_expression`. Within this function, the line `result = eval(s)` poses a security risk as it can directly execute user-provided commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48050
- https://gist.github.com/AfterSnows/0ad9d233a9d2a5b7e6e5273e2e23508d
- https://github.com/modelscope/agentscope
- https://github.com/modelscope/agentscope/blob/main/src/agentscope/web/workstation/workflow_utils.py#L11
- https://rumbling-slice-eb0.notion.site/Unauthenticated-Remote-Code-Execution-via-The-use-of-eval-in-is_callable_expression-and-sanitize_nod-cd4ea6c576da4e0b965ef596855c298d
