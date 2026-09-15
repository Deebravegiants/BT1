# [H] Path Traversal in mlflow/mlflow

## Summary
Severity: High
Advisory: BIT-mlflow-2024-8859
Aliases: CVE-2024-8859, GHSA-4rqf-8pfm-p36r, PYSEC-2026-1638
Ecosystem: Bitnami
Published: 2025-08-06
Source: https://osv.dev/vulnerability/BIT-mlflow-2024-8859
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=2.15.1 <2.16.0

## Details
A path traversal vulnerability exists in mlflow/mlflow version 2.15.1. When users configure and use the dbfs service, concatenating the URL directly into the file protocol results in an arbitrary file read vulnerability. This issue occurs because only the path part of the URL is checked, while parts such as query and parameters are not handled. The vulnerability is triggered if the user has configured the dbfs service, and during usage, the service is mounted to a local directory.

## References
- https://github.com/mlflow/mlflow/commit/7791b8cdd595f21b5f179c7b17e4b5eb5cbbe654
- https://huntr.com/bounties/2259b88b-a0c6-4c7c-b434-6aacf6056dcb
- https://nvd.nist.gov/vuln/detail/CVE-2024-8859
