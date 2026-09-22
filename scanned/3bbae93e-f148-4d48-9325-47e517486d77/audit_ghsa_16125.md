# [M] Langflow vulnerable to remote code execution

## Summary
Severity: Medium
Advisory: GHSA-5p5r-57fx-pmfr
CVE: CVE-2024-48061
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-5p5r-57fx-pmfr
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0

## Details
langflow <=1.0.18 is vulnerable to Remote Code Execution (RCE) as any component provided the code functionality and the components run on the local machine rather than in a sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48061
- https://github.com/langflow-ai/langflow/issues/696
- https://gist.github.com/AfterSnows/1e58257867002462923fd62dde2b5d61
- https://github.com/langflow-ai/langflow
- https://rumbling-slice-eb0.notion.site/There-is-a-Remote-Code-Execution-RCE-vulnerability-in-the-repository-https-github-com-langflow-a-105e3cda9e8c800fac92f1b571bd40d8
