# [M] MLflow is vulnerable to Stored Cross-Site Scripting (XSS) caused by unsafe parsing of YAML-based MLmodel artifacts in its web interface

## Summary
Severity: Medium
Advisory: GHSA-fh64-r2vc-xvhr
CVE: CVE-2026-33865
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-fh64-r2vc-xvhr
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.11.1

## Details
MLflow is vulnerable to Stored Cross-Site Scripting (XSS) caused by unsafe parsing of YAML-based MLmodel artifacts in its web interface. An authenticated attacker can upload a malicious MLmodel file containing a payload that executes when another user views the artifact in the UI. This allows actions such as session hijacking or performing operations on behalf of the victim. 

This issue affects MLflow version through 3.10.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33865
- https://github.com/mlflow/mlflow/pull/21435
- https://github.com/mlflow/mlflow/commit/aca4dd0ec88a12f7655155c224371280e9b45dda
- https://afine.com/blogs/attacking-mlflow-how-ml-artifacts-become-attack-vectors
- https://cert.pl/en/posts/2026/04/CVE-2026-33865
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2026-93.yaml
