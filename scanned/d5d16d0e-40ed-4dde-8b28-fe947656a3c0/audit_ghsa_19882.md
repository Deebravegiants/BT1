# [M] Azure PromptFlow remote code execution related to Jinja templates

## Summary
Severity: Medium
Advisory: GHSA-gprr-v9f2-px3c
CVE: CVE-2025-24986
CWE: CWE-653
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-gprr-v9f2-px3c
Type: github-advisory

## Affected
- PyPI: `promptflow-tools` — affected >=0 <1.6.0
- PyPI: `promptflow-core` — affected >=0 <1.17.2

## Details
Improper isolation or compartmentalization in Azure PromptFlow allows an unauthorized attacker to execute code over a network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24986
- https://github.com/microsoft/promptflow/commit/5f4a41ab4cb15607ade7f26138b0b863b4e4eb0a
- https://github.com/microsoft/promptflow/commit/625061724c51533d28fe6e0e3014b1042afdb07f
- https://github.com/microsoft/promptflow
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-24986
