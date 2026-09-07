# [C] BentoML deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9g44-gwvm-hc44
CVE: CVE-2024-9070
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-9g44-gwvm-hc44
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0

## Details
A deserialization vulnerability exists in BentoML's runner server in bentoml/bentoml versions <=1.3.4.post1. By setting specific parameters, an attacker can execute unauthorized arbitrary code on the server, causing severe harm. The vulnerability is triggered when the args-number parameter is greater than 1, leading to automatic deserialization and arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9070
- https://github.com/bentoml/BentoML
- https://github.com/bentoml/BentoML/blob/a6f5f937be6ec278f3d4f3bbc6f3c8f9564820d7/src/bentoml/_internal/server/runner_app.py#L297
- https://github.com/bentoml/BentoML/blob/v1.4.5/src/bentoml/_internal/server/runner_app.py#L301
- https://huntr.com/bounties/7be6fc22-be18-44ee-a001-ac7158d5e1a5
