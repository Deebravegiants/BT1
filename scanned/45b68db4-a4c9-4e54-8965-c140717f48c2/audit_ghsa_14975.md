# [H] MLFlow unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-cv6c-7963-wxcg
CVE: CVE-2024-37060
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-cv6c-7963-wxcg
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=1.27.0

## Details
Deserialization of untrusted data can occur in versions of the MLflow platform running version 1.27.0 or newer, enabling a maliciously crafted Recipe to execute arbitrary code on an end user’s system when run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37060
- https://github.com/mlflow/mlflow
- https://hiddenlayer.com/sai-security-advisory/mlflow-june2024
