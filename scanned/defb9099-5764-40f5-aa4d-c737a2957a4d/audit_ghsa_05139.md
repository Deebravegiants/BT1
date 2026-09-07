# [H] Apache Airflow: Authenticated users can bypass the `is_safe_url` check

## Summary
Severity: High
Advisory: GHSA-6hcw-qqr8-pjj8
CVE: CVE-2026-40961
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-6hcw-qqr8-pjj8
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.2

## Details
A bug in the login redirect route in Apache Airflow allowed authenticated users to craft URLs that bypassed the `is_safe_url` check, enabling redirection from a trusted Airflow domain to an attacker-controlled origin. Users are advised to upgrade to `apache-airflow` 3.2.2 or later. As a defense-in-depth mitigation, deployment operators can place Airflow behind a reverse proxy that strips off-domain `next=` query parameters before they reach the login endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40961
- https://github.com/apache/airflow/pull/65557
- https://github.com/apache/airflow
- https://lists.apache.org/thread/qmt8ksh7gty6b8hr9w294t94j36jdv1q
- http://www.openwall.com/lists/oss-security/2026/05/31/2
