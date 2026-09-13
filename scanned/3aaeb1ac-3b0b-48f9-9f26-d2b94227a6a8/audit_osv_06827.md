# [H] Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: BIT-mlflow-2023-6976
Aliases: CVE-2023-6976, GHSA-wv8q-4f85-2p8p, PYSEC-2026-1662
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mlflow-2023-6976
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <2.9.2

## Details
This vulnerability is capable of writing arbitrary files into arbitrary locations on the remote filesystem in the context of the server process.

## References
- https://github.com/mlflow/mlflow/commit/5044878da0c1851ccfdd5c0a867157ed9a502fbc
- https://huntr.com/bounties/2408a52b-f05b-4cac-9765-4f74bac3f20f
- https://nvd.nist.gov/vuln/detail/CVE-2023-6976
