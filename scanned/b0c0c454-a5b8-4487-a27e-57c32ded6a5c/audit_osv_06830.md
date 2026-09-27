# [H] BIT-mlflow-2024-37052

## Summary
Severity: High
Advisory: BIT-mlflow-2024-37052
Aliases: CVE-2024-37052, GHSA-76cg-cfhx-373f, PYSEC-2026-1643
Ecosystem: Bitnami
Published: 2024-06-08
Source: https://osv.dev/vulnerability/BIT-mlflow-2024-37052
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=1.1.0 <2.14.2

## Details
Deserialization of untrusted data can occur in versions of the MLflow platform running version 1.1.0 or newer, enabling a maliciously uploaded scikit-learn model to run arbitrary code on an end user’s system when interacted with.

## References
- https://hiddenlayer.com/sai-security-advisory/mlflow-june2024
- https://nvd.nist.gov/vuln/detail/CVE-2024-37052
