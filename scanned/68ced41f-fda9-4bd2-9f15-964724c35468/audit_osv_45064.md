# [H] PYSEC-2024-239

## Summary
Severity: High
Advisory: PYSEC-2024-239
Aliases: BIT-mlflow-2024-0520, CVE-2024-0520, GHSA-5q6c-ffvg-xcm9
Ecosystem: PyPI
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/PYSEC-2024-239
Type: osv

## Affected
- PyPI: `mlflow` — affected >=0 <400c226953b4568f4361bc0a0c223511652c2b9d, >=0 <2.9.0

## Details
A vulnerability in mlflow/mlflow version 8.2.1 allows for remote code execution due to improper neutralization of special elements used in an OS command ('Command Injection') within the `mlflow.data.http_dataset_source.py` module. Specifically, when loading a dataset from a source URL with an HTTP scheme, the filename extracted from the `Content-Disposition` header or the URL path is used to generate the final file path without proper sanitization. This flaw enables an attacker to control the file path fully by utilizing path traversal or absolute path techniques, such as '../../tmp/poc.txt' or '/tmp/poc.txt', leading to arbitrary file write. Exploiting this vulnerability could allow a malicious user to execute commands on the vulnerable machine, potentially gaining access to data and model information. The issue is fixed in version 2.9.0.

## References
- https://huntr.com/bounties/93e470d7-b6f0-409b-af63-49d3e2a26dbc
- https://github.com/mlflow/mlflow/commit/400c226953b4568f4361bc0a0c223511652c2b9d
- https://huntr.com/bounties/93e470d7-b6f0-409b-af63-49d3e2a26dbc
- https://huntr.com/bounties/93e470d7-b6f0-409b-af63-49d3e2a26dbc
- https://huntr.com/bounties/93e470d7-b6f0-409b-af63-49d3e2a26dbc
- https://github.com/advisories/GHSA-5q6c-ffvg-xcm9
