# [C] MLflow: Improper Origin Validation in MLflow Assistant /ajax-api Endpoints Enables Browser-Mediated Local Command Execution

## Summary
Severity: Critical
Advisory: GHSA-67c5-x5mf-rppq
CVE: CVE-2026-2611
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-67c5-x5mf-rppq
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=3.9.0 <3.10.0

## Details
In MLflow version 3.9.0, the MLflow Assistant feature introduced improper origin validation in its /ajax-api endpoints. This vulnerability allows a remote attacker to exploit cross-origin requests from a malicious webpage to interact with the MLflow Assistant running on a victim's local machine. By bypassing the loopback-only restriction, the attacker can modify the Assistant's configuration to enable full access, which in turn allows the execution of arbitrary commands via the Claude Code sub-agent. This issue is resolved in version 3.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2611
- https://github.com/mlflow/mlflow/commit/8f9c8a53af90842944101eb8b7d60706822c81bc
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/8462addd-b464-4a84-b6a2-5529604e6e5a
