# [H] mlflow vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-m49c-5c52-6696
CVE: CVE-2024-1594
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-m49c-5c52-6696
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0

## Details
A path traversal vulnerability exists in the mlflow/mlflow repository, specifically within the handling of the `artifact_location` parameter when creating an experiment. Attackers can exploit this vulnerability by using a fragment component `#` in the artifact location URI to read arbitrary files on the server in the context of the server's process. This issue is similar to CVE-2023-6909 but utilizes a different component of the URI to achieve the same effect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1594
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/blob/b929a3e727dc48a1eb19b7e954b7897ac09ad3ec/mlflow/utils/uri.py#L246
- https://huntr.com/bounties/424b6f6b-e778-4a2b-b860-39730d396f3e
