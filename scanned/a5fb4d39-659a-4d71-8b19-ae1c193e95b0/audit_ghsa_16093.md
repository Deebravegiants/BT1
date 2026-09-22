# [H] MLflow's excessive directory permissions allow local privilege escalation

## Summary
Severity: High
Advisory: GHSA-qpgc-w4mg-6v92
CVE: CVE-2024-27134
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-qpgc-w4mg-6v92
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.16.0

## Details
Excessive directory permissions in MLflow leads to local privilege escalation when using spark_udf. This behavior can be exploited by a local attacker to gain elevated permissions by using a ToCToU attack. The issue is only relevant when the spark_udf() MLflow API is called.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27134
- https://github.com/mlflow/mlflow/pull/10874
- https://github.com/mlflow/mlflow/commit/0b1d995d66a678153e01ed3040f3f4dfc16a0d6b
- https://github.com/mlflow/mlflow
