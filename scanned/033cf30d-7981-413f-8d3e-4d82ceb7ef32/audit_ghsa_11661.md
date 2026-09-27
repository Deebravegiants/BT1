# [H] Apache Airflow: Path of session token in cookie does not consider base_url - session hijacking via co-hosted applications

## Summary
Severity: High
Advisory: GHSA-4fhm-p86v-hwpx
CVE: CVE-2026-28779
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-4fhm-p86v-hwpx
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.1.8

## Details
Apache Airflow versions 3.1.0 through 3.1.7 session token (_token) in cookies is set to path=/ regardless of the configured [webserver] base_url or [api] base_url.
This allows any application co-hosted under the same domain to capture valid Airflow session tokens from HTTP request headers, allowing full session takeover without attacking Airflow itself.

Users are recommended to upgrade to Apache Airflow 3.1.8 or later, which resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28779
- https://github.com/apache/airflow/pull/62771
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-16.yaml
- https://lists.apache.org/thread/r4n5znb8mcq14wo9v8ndml36nxlksdqb
- http://www.openwall.com/lists/oss-security/2026/03/17/3
