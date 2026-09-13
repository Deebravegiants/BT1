# [C] Langflow Unauth RCE

## Summary
Severity: Critical
Advisory: GHSA-rvqx-wpfh-mfx7
CVE: CVE-2025-3248
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:A (CVSS_V4)
Published: 2025-06-17
Source: https://github.com/advisories/GHSA-rvqx-wpfh-mfx7
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.3.0
- PyPI: `langflow-base` — affected >=0 <0.3.0

## Details
Langflow versions prior to 1.3.0 are susceptible to code injection in the /api/v1/validate/code endpoint. A remote and unauthenticated attacker can send crafted HTTP requests to execute arbitrary code.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-rvqx-wpfh-mfx7
- https://nvd.nist.gov/vuln/detail/CVE-2025-3248
- https://github.com/langflow-ai/langflow/pull/6911
- https://github.com/langflow-ai/langflow/commit/faac4db133de32fcb6d483fa9ff52f40ce42bdc0
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/releases/tag/1.3.0
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-3248
- https://www.horizon3.ai/attack-research/disclosures/unsafe-at-any-speed-abusing-python-exec-for-unauth-rce-in-langflow-ai
- https://www.vulncheck.com/advisories/langflow-unauthenticated-rce
