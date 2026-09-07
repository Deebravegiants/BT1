# [M] MLflow Cross-Site Request Forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-969w-gqqr-g6j3
CVE: CVE-2025-1473
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-969w-gqqr-g6j3
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=2.17.0 <2.20.3

## Details
A Cross-Site Request Forgery (CSRF) vulnerability exists in the Signup feature of mlflow/mlflow versions 2.17.0 to 2.20.1. This vulnerability allows an attacker to create a new account, which may be used to perform unauthorized actions on behalf of the malicious user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1473
- https://github.com/mlflow/mlflow/commit/ecfa61cb43d3303589f3b5834fd95991c9706628
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/43dc50b6-7d1e-41b9-9f97-f28809df1d45
