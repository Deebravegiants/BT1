# [H] MLFlow unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-ghv6-9r9j-wh4j
CVE: CVE-2024-37054
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-ghv6-9r9j-wh4j
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0.9.0

## Details
Deserialization of untrusted data can occur in versions of the MLflow platform running version 0.9.0 or newer, enabling a maliciously uploaded PyFunc model to run arbitrary code on an end user’s system when interacted with.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37054
- https://github.com/mlflow/mlflow
- https://hiddenlayer.com/sai-security-advisory/mlflow-june2024
