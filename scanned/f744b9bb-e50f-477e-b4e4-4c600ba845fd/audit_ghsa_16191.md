# [C] MLFlow Cross-site Scripting vulnerability leads to client-side Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-3v79-q7ph-j75h
CVE: CVE-2024-27133
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-24
Source: https://github.com/advisories/GHSA-3v79-q7ph-j75h
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.10.0

## Details
Insufficient sanitization in MLflow leads to XSS when running a recipe that uses an untrusted dataset. This issue leads to a client-side RCE when running the recipe in Jupyter Notebook. The vulnerability stems from lack of sanitization over dataset table fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27133
- https://github.com/mlflow/mlflow/pull/10893
- https://github.com/mlflow/mlflow/commit/c43823750bffa5b6abcc086683b15a068513b67b
- https://github.com/mlflow/mlflow/commit/cfa71879a884cc3520e23ccab998c9aa78fdf2b1
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2024-241.yaml
- https://research.jfrog.com/vulnerabilities/mlflow-untrusted-dataset-xss-jfsa-2024-000631932
