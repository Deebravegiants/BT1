# [H] Guardrails has an arbitrary code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-w392-75q8-vr67
CVE: CVE-2024-45858
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-w392-75q8-vr67
Type: github-advisory

## Affected
- PyPI: `guardrails-ai` — affected >=0.2.9 <0.5.10

## Details
An arbitrary code execution vulnerability exists in versions 0.2.9 up to 0.5.10 of the Guardrails AI Guardrails framework because of the way it validates XML files. If a victim user loads a maliciously crafted XML file containing Python code, the code will be passed to an eval function, causing it to execute on the user's machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45858
- https://github.com/guardrails-ai/guardrails/commit/ab12701e8c3ef41273ff9b3912f2e4e28ae8306f
- https://github.com/guardrails-ai/guardrails
- https://hiddenlayer.com/sai-security-advisory/2024-09-guardrails
