# [C] MLflow: Environment variable injection in AI Gateway secrets enables server-side credential exfiltration

## Summary
Severity: Critical
Advisory: GHSA-g35p-px32-whv6
CVE: CVE-2026-4035
CWE: CWE-201
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-g35p-px32-whv6
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.11.0

## Details
A vulnerability in mlflow/mlflow versions prior to 3.11.0 allows for the resolution of environment variables in AI Gateway secrets, which can be exploited to exfiltrate sensitive server-side environment credentials to an attacker-controlled endpoint. This issue arises because the `api_key` field in gateway secrets can accept `$ENV_VAR` references, which are resolved against the MLflow server's environment during runtime. The resolved secrets are then sent in provider authentication headers to the configured upstream `api_base`. This vulnerability can be exploited by low-privileged authenticated users in basic-auth deployments or by unauthenticated users in default deployments without `basic-auth`. The impact includes potential leakage of sensitive credentials such as cloud artifact credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`), which could lead to artifact poisoning and cross-boundary code execution in downstream environments. The issue is fixed in version 3.11.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4035
- https://github.com/mlflow/mlflow/commit/4a3f2f720cb4f058c9e0c5b883e0acc9ab64a7f3
- https://access.redhat.com/security/cve/CVE-2026-4035
- https://bugzilla.redhat.com/show_bug.cgi?id=2484318
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/f8e591a0-0f19-4910-b82e-16c9956f2233
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4035.json
