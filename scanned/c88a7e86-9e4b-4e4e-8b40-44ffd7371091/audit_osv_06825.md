# [C] Command Injection

## Summary
Severity: Critical
Advisory: BIT-mlflow-2023-6940
Aliases: CVE-2023-6940, GHSA-hvc6-42vf-jhf8, PYSEC-2026-1652
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mlflow-2023-6940
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <2.9.2

## Details
with only one user interaction(download a malicious config), attackers can gain full command execution on the victim system.

## References
- https://github.com/mlflow/mlflow/commit/5139b1087d686fa52e2b087e09da66aff86297b1
- https://huntr.com/bounties/c6f59480-ce47-4f78-a3dc-4bd8ca15029c
- https://nvd.nist.gov/vuln/detail/CVE-2023-6940
