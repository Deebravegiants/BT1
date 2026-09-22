# [H] langflow has vulnerability in PythonCodeTool component

## Summary
Severity: High
Advisory: GHSA-56m6-4mhw-h3g5
CVE: CVE-2024-42835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-56m6-4mhw-h3g5
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0

## Details
langflow v1.0.12 was discovered to contain a remote code execution (RCE) vulnerability via the PythonCodeTool component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42835
- https://github.com/langflow-ai/langflow/issues/2908
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2024-279.yaml
