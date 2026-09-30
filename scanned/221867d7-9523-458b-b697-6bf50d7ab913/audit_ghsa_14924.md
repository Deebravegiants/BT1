# [H] MLFlow unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-j8mg-pqc5-x9gj
CVE: CVE-2024-37057
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-j8mg-pqc5-x9gj
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=2.0.0rc0

## Details
Deserialization of untrusted data can occur in versions of the MLflow platform running version 2.0.0rc0 or newer, enabling a maliciously uploaded Tensorflow model to run arbitrary code on an end user’s system when interacted with.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37057
- https://github.com/mlflow/mlflow
- https://hiddenlayer.com/sai-security-advisory/mlflow-june2024
