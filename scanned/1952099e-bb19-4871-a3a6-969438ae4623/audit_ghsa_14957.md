# [H] Langflow remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-qg33-x2c5-6p44
CVE: CVE-2024-37014
CWE: CWE-913, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-qg33-x2c5-6p44
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.0.15

## Details
Langflow allows remote code execution if untrusted users are able to reach the "POST /api/v1/custom_component" endpoint and provide a Python script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37014
- https://github.com/langflow-ai/langflow/issues/1973
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2024-177.yaml
