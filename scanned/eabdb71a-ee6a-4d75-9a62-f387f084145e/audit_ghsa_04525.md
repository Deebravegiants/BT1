# [M] MLflow: Any authenticated user can enumerate all gateway secrets, endpoints, and model definitions

## Summary
Severity: Medium
Advisory: GHSA-r5m9-wm49-959f
CVE: CVE-2026-3198
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-02
Source: https://github.com/advisories/GHSA-r5m9-wm49-959f
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.11.0rc0

## Details
MLflow 3.9.0 with basic-auth (`--app-name basic-auth`) fails to enforce authorization checks for multiple Gateway API 'list' endpoints. Specifically, the `BEFORE_REQUEST_HANDLERS` dictionary in `mlflow/server/auth/__init__.py` does not include entries for `ListGatewaySecretInfos`, `ListGatewayEndpoints`, and `ListGatewayModelDefinitions`. This allows any authenticated user, regardless of their assigned permissions, to enumerate all gateway secrets, endpoints, and model definitions. This vulnerability exposes sensitive information, such as API keys, endpoint configurations, and proprietary model definitions, to unauthorized users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3198
- https://github.com/mlflow/mlflow/commit/6989066af33fdcb03588fd71a1a67f8fc5ef12c9
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/e57db731-97d3-40c3-a429-831ee959807f
