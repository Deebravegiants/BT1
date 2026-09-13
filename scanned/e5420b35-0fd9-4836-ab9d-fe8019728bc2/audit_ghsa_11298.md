# [H] MLflow has a command injection in mlflow/sagemaker/__init__.py

## Summary
Severity: High
Advisory: GHSA-xch3-2f9x-wh9f
CVE: CVE-2025-14287
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-xch3-2f9x-wh9f
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.8.0rc0

## Details
A command injection vulnerability exists in mlflow/mlflow versions before v3.7.0, specifically in the `mlflow/sagemaker/__init__.py` file at lines 161-167. The vulnerability arises from the direct interpolation of user-supplied container image names into shell commands without proper sanitization, which are then executed using `os.system()`. This allows attackers to execute arbitrary commands by supplying malicious input through the `--container` parameter of the CLI. The issue affects environments where MLflow is used, including development setups, CI/CD pipelines, and cloud deployments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14287
- https://github.com/mlflow/mlflow/pull/19277
- https://github.com/mlflow/mlflow/commit/8b8792a7034fb33a14b0b31cabcaa9b912d3485f
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.8.0rc0
- https://huntr.com/bounties/229cd526-41aa-4819-b6f0-e2d0371c89e3
