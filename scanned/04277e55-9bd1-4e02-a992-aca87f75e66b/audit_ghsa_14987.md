# [H] MLFlow improper input validation

## Summary
Severity: High
Advisory: GHSA-pqcv-qw2r-r859
CVE: CVE-2024-37061
CWE: CWE-20, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-pqcv-qw2r-r859
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=1.11.0

## Details
Remote Code Execution can occur in versions of the MLflow platform running version 1.11.0 or newer, enabling a maliciously crafted MLproject to execute arbitrary code on an end user’s system when run due to unfiltered input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37061
- https://github.com/mlflow/mlflow
- https://hiddenlayer.com/sai-security-advisory/mlflow-june2024
