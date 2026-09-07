# [M] apache-airflow-providers-keycloak: Missing OAuth 2.0 State and PKCE Enables Login CSRF and Session Fixation

## Summary
Severity: Medium
Advisory: GHSA-5w6h-pjw6-wvc6
CVE: CVE-2026-40948
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-5w6h-pjw6-wvc6
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-keycloak` — affected >=0.0.1 <0.7.0

## Details
The Keycloak authentication manager in `apache-airflow-providers-keycloak` did not generate or validate the OAuth 2.0 `state` parameter on the login / login-callback flow, and did not use PKCE. An attacker with a Keycloak account in the same realm could deliver a crafted callback URL to a victim's browser and cause the victim to be logged into the attacker's Airflow session (login-CSRF / session fixation), where any credentials the victim subsequently stored in Airflow Connections would be harvestable by the attacker. Users are advised to upgrade `apache-airflow-providers-keycloak` to 0.7.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40948
- https://github.com/apache/airflow/pull/64114
- https://github.com/apache/airflow
- https://lists.apache.org/thread/kc0odpr70hbqhdb9ksnz42fkqz2xld9q
- http://www.openwall.com/lists/oss-security/2026/04/17/14
