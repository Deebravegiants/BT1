# [M] Apache Airflow: Auth manager doesn't invalidate JWT tokens after users click logout

## Summary
Severity: Medium
Advisory: GHSA-vr7m-c6v4-8cx8
CVE: CVE-2026-48726
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-vr7m-c6v4-8cx8
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.2

## Details
A bug in Apache Airflow's auth manager logout handling left previously-issued JWT tokens valid after the user clicked logout in the UI: the logout flow for `FabAuthManager` and `KeycloakAuthManager` did not actually reach the underlying `revoke_token()` call, so the JWT remained accepted by the API server until its natural expiry. An attacker holding a previously-issued JWT for a logged-out user could continue to make authenticated API calls as that user. Affects deployments configured with `FabAuthManager` or `KeycloakAuthManager` (the bug does not affect SimpleAuthManager). This is a residual gap in the fix for CVE-2025-57735, which addressed cookie-side invalidation in PR #57992 / PR #61339 but did not cover the provider-side `revoke_token()` reachability in the FAB / Keycloak code paths. Users who already upgraded for CVE-2025-57735 should additionally upgrade to `apache-airflow` 3.2.2 or later to cover the FAB / Keycloak logout paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48726
- https://github.com/apache/airflow/pull/67289
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-187.yaml
- https://lists.apache.org/thread/630jg4z6cjkv4m2yv2ljgmf1zhdj1vqx
- https://www.cve.org/CVERecord?id=CVE-2025-57735
