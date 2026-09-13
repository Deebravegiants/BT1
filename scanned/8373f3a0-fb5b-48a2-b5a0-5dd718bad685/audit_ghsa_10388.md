# [M] MLflow is vulnerable to an authorization bypass affecting the AJAX endpoint

## Summary
Severity: Medium
Advisory: GHSA-46r5-x6jq-v8g6
CVE: CVE-2026-33866
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-46r5-x6jq-v8g6
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.11.0rc0

## Details
MLflow is vulnerable to an authorization bypass affecting the AJAX endpoint used to download saved model artifacts. Due to missing access‑control validation, a user without permissions to a given experiment can directly query this endpoint and retrieve model artifacts they are not authorized to access.

 
This issue affects MLflow version through 3.10.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33866
- https://github.com/mlflow/mlflow/pull/21708
- https://github.com/mlflow/mlflow/commit/005b959cacda05d1423356cfcbd9ebeda8ff96a7
- https://afine.com/blogs/attacking-mlflow-how-ml-artifacts-become-attack-vectors
- https://cert.pl/en/posts/2026/04/CVE-2026-33865
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2026-94.yaml
