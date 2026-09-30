# [C] PYSEC-2024-243

## Summary
Severity: Critical
Advisory: PYSEC-2024-243
Aliases: BIT-mlflow-2024-3573, CVE-2024-3573, GHSA-hq88-wg7q-gp4g
Ecosystem: PyPI
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/PYSEC-2024-243
Type: osv

## Affected
- PyPI: `mlflow` — affected >=0 <438a450714a3ca06285eeea34bdc6cf79d7f6cbc, >=0 <2.10.0

## Details
mlflow/mlflow is vulnerable to Local File Inclusion (LFI) due to improper parsing of URIs, allowing attackers to bypass checks and read arbitrary files on the system. The issue arises from the 'is_local_uri' function's failure to properly handle URIs with empty or 'file' schemes, leading to the misclassification of URIs as non-local. Attackers can exploit this by crafting malicious model versions with specially crafted 'source' parameters, enabling the reading of sensitive files within at least two directory levels from the server's root.

## References
- https://huntr.com/bounties/8ea058a7-4ef8-4baf-9198-bc0147fc543c
- https://github.com/mlflow/mlflow/commit/438a450714a3ca06285eeea34bdc6cf79d7f6cbc
- https://huntr.com/bounties/8ea058a7-4ef8-4baf-9198-bc0147fc543c
- https://huntr.com/bounties/8ea058a7-4ef8-4baf-9198-bc0147fc543c
- https://github.com/advisories/GHSA-hq88-wg7q-gp4g
