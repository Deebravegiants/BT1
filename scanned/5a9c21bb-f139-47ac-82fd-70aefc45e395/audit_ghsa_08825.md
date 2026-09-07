# [M] MLflow authenticated users can enumerate any registered model versions due to lack of per-model permissions checks

## Summary
Severity: Medium
Advisory: GHSA-w5xq-c4pf-ghq7
CVE: CVE-2026-2734
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-w5xq-c4pf-ghq7
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.10.0

## Details
In mlflow/mlflow versions up to 3.9.0, the `SearchModelVersions` REST API endpoint and the `mlflowSearchModelVersions` GraphQL query lack proper per-model authorization checks when basic authentication is enabled. This allows any authenticated user to enumerate all model versions across all registered models, regardless of their permission level. The issue arises due to the absence of `SearchModelVersions` in the `BEFORE_REQUEST_VALIDATORS` and `AFTER_REQUEST_HANDLERS` for the REST API, and its omission from `GraphQLAuthorizationMiddleware.PROTECTED_FIELDS` for GraphQL. This vulnerability can expose sensitive information such as model names, version descriptions, source URIs, tags, and other metadata, potentially revealing proprietary or confidential details in multi-tenant environments. The issue is resolved in version 3.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2734
- https://github.com/mlflow/mlflow/commit/6989066af33fdcb03588fd71a1a67f8fc5ef12c9
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/d632f783-b2c7-4a3b-af5e-1d693e841c08
