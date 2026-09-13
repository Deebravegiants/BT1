# [M] Apache Airflow has a Sensitive Cookie in HTTPS Session Without 'Secure' Attribute

## Summary
Severity: Medium
Advisory: GHSA-95v7-h9j5-gvjr
CVE: CVE-2026-41017
CWE: CWE-614
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-95v7-h9j5-gvjr
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.2

## Details
Apache Airflow's `JWTRefreshMiddleware` set the JWT auth cookie without the `Secure` flag, so deployments running the Airflow API server behind an HTTPS-terminating reverse proxy (e.g. nginx / Envoy / a managed load balancer that terminates TLS and forwards plaintext to the API server, the default cloud-native topology) would have the user's session JWT replayed over any cleartext HTTP request to the same host. A network-positioned attacker (Wi-Fi MITM, hostile LAN, captive-portal proxy) could induce a logged-in user's browser to issue an HTTP request to the deployment's hostname and capture the JWT cookie out of that request, then replay it against the authenticated API. Affects deployments where the Airflow API server is reached through a TLS-terminating proxy and the cookie's secure-by-default protection is load-bearing for session integrity. Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41017
- https://github.com/apache/airflow/pull/65348
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-171.yaml
- https://lists.apache.org/thread/9jx0sk49c1250zflx0q3clc717qgjdch
- http://www.openwall.com/lists/oss-security/2026/05/31/6
