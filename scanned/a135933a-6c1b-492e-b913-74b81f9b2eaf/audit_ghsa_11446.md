# [H] MLFlow allows Tracing + Assessments Access

## Summary
Severity: High
Advisory: GHSA-g6pg-52vf-843h
CVE: CVE-2025-15381
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-g6pg-52vf-843h
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0

## Details
In the latest version of mlflow/mlflow, when the `basic-auth` app is enabled, tracing and assessment endpoints are not protected by permission validators. This allows any authenticated user, including those with `NO_PERMISSIONS` on the experiment, to read trace information and create assessments for traces they should not have access to. This vulnerability impacts confidentiality by exposing trace metadata and integrity by allowing unauthorized creation of assessments. Deployments using `mlflow server --app-name=basic-auth` are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15381
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/blob/b569ebc74c14af593c326143bee2df44a5d59edf/mlflow/server/auth/__init__.py#L752
- https://huntr.com/bounties/149fb2f9-ef4b-4136-a25c-20563451904c
