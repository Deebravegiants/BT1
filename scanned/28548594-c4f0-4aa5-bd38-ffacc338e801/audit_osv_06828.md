# [H] Path Traversal via Parameter Smuggling in mlflow/mlflow

## Summary
Severity: High
Advisory: BIT-mlflow-2024-1593
Aliases: CVE-2024-1593, GHSA-f42m-mvfv-cgw5, PYSEC-2026-1649
Ecosystem: Bitnami
Published: 2025-02-04
Source: https://osv.dev/vulnerability/BIT-mlflow-2024-1593
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <2.11.3

## Details
A path traversal vulnerability exists in the mlflow/mlflow repository due to improper handling of URL parameters. By smuggling path traversal sequences using the ';' character in URLs, attackers can manipulate the 'params' portion of the URL to gain unauthorized access to files or directories. This vulnerability allows for arbitrary data smuggling into the 'params' part of the URL, enabling attacks similar to those described in previous reports but utilizing the ';' character for parameter smuggling. Successful exploitation could lead to unauthorized information disclosure or server compromise.

## References
- https://huntr.com/bounties/dbdc6bd6-d09a-46f2-9d9c-5138a14b6e31
- https://nvd.nist.gov/vuln/detail/CVE-2024-1593
