# [H] MLFlow is vulnerable to DNS rebinding attacks due to a lack of Origin header validation

## Summary
Severity: High
Advisory: GHSA-pgqp-8h46-6x4j
CVE: CVE-2025-14279
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-12
Source: https://github.com/advisories/GHSA-pgqp-8h46-6x4j
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.5.0

## Details
MLFlow versions up to and including 3.4.0 are vulnerable to DNS rebinding attacks due to a lack of Origin header validation in the MLFlow REST server. This vulnerability allows malicious websites to bypass Same-Origin Policy protections and execute unauthorized calls against REST endpoints. An attacker can query, update, and delete experiments via the affected endpoints, leading to potential data exfiltration, destruction, or manipulation. The issue is resolved in version 3.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14279
- https://github.com/mlflow/mlflow/pull/17910
- https://github.com/mlflow/mlflow/commit/b0ffd289e9b0d0cc32c9e3a9b9f3843ae83dbec3
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/ef478f72-2e4f-44dc-8055-fc06bef03108
