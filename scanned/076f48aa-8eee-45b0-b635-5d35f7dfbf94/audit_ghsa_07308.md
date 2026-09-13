# [H] MLflow: trace API endpoints lack proper authorization validators

## Summary
Severity: High
Advisory: GHSA-2cm6-r77w-6g96
CVE: CVE-2026-8147
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2cm6-r77w-6g96
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=2.14.0rc0 <3.13.0rc0

## Details
In MLflow versions prior to 3.13.0, when running with authentication enabled, the trace API endpoints lack proper authorization validators. This allows any authenticated user to bypass experiment-level authorization controls on all trace operations, including reading, deleting, and modifying traces on experiments they do not have permission to access. The issue arises from the `_before_request` handler, which does not register authorization validators for trace endpoints, resulting in requests proceeding without validation. This vulnerability can expose sensitive data, destroy audit logs, and allow unauthorized modifications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8147
- https://github.com/mlflow/mlflow/pull/23014
- https://github.com/mlflow/mlflow/commit/f9b1eb510478570609ef451984a255775aa4b937
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.13.0
- https://huntr.com/bounties/b00c3ddd-373e-492f-9bf0-41a28bb21ed5
