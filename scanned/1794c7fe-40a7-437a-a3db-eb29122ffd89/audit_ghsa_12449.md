# [H] Information exposure in MLflow

## Summary
Severity: High
Advisory: GHSA-wqxf-447m-6f5f
CVE: CVE-2023-43472
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-wqxf-447m-6f5f
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.9.0

## Details
An issue in MLFlow versions 2.8.1 and before allows a remote attacker to obtain sensitive information via a crafted request to REST API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43472
- https://github.com/mlflow/mlflow
- https://mlflow.org/news/2023/12/06/2.9.0-release/index.html
- https://www.contrastsecurity.com/security-influencers/discovering-mlflow-framework-zero-day-vulnerability-machine-language-model-security-contrast-security
