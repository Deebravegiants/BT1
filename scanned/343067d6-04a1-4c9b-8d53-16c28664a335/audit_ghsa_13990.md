# [H] mflow vulnerable to directory traversal

## Summary
Severity: High
Advisory: GHSA-wc6j-5g83-xfm6
CVE: CVE-2023-30172
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-wc6j-5g83-xfm6
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.0.0rc0

## Details
A directory traversal vulnerability in the /get-artifact API method of the mlflow platform prior to v2.0.0 allows attackers to read arbitrary files on the server via the path parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30172
- https://github.com/mlflow/mlflow/issues/7166
- https://github.com/mlflow/mlflow/issues/7166#issuecomment-1541543234
- https://github.com/mlflow/mlflow/pull/7170
- https://github.com/mlflow/mlflow/commit/ac4b697bb0bb8a331944dca63f4235b4bf602ab8
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/commits/v2.0.0?after=00c3b0a350a28c25b16fbb7feddb8147a919ce18+69&branch=v2.0.0&qualified_name=refs%2Ftags%2Fv2.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2023-70.yaml
