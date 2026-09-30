# [C] Path Traversal: '\..\filename'

## Summary
Severity: Critical
Advisory: BIT-mlflow-2023-6975
Aliases: CVE-2023-6975, GHSA-hh8p-p8mp-gqhm, PYSEC-2026-422
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mlflow-2023-6975
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <2.9.2

## Details
A malicious user could use this issue to get command execution on the vulnerable machine and get access to data & models information.

## References
- https://github.com/mlflow/mlflow/commit/b9ab9ed77e1deda9697fe472fb1079fd428149ee
- https://huntr.com/bounties/029a3824-cee3-4cf1-b260-7138aa539b85
- https://nvd.nist.gov/vuln/detail/CVE-2023-6975
