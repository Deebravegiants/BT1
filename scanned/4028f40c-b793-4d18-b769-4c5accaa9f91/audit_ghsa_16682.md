# [H] MLflow has a Local File Read/Path Traversal bypass

## Summary
Severity: High
Advisory: GHSA-rfqq-wq6w-72jm
CVE: CVE-2024-3848
CWE: CWE-22, CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-rfqq-wq6w-72jm
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=2.9.2 <2.12.1

## Details
A path traversal vulnerability exists in mlflow/mlflow version 2.11.0, identified as a bypass for the previously addressed CVE-2023-6909. The vulnerability arises from the application's handling of artifact URLs, where a '#' character can be used to insert a path into the fragment, effectively skipping validation. This allows an attacker to construct a URL that, when processed, ignores the protocol scheme and uses the provided path for filesystem access. As a result, an attacker can read arbitrary files, including sensitive information such as SSH and cloud keys, by exploiting the way the application converts the URL into a filesystem path. The issue stems from insufficient validation of the fragment portion of the URL, leading to arbitrary file read through path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3848
- https://github.com/mlflow/mlflow/commit/f8d51e21523238280ebcfdb378612afd7844eca8
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2024-244.yaml
- https://huntr.com/bounties/8d5aadaa-522f-4839-b41b-d7da362dd610
