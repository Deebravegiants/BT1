# [M] Apache Airflow: Sensitive configuration for providers displayed when "non-sensitive-only" config used

## Summary
Severity: Medium
Advisory: GHSA-2522-mrjc-m688
CVE: CVE-2024-31869
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-18
Source: https://github.com/advisories/GHSA-2522-mrjc-m688
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.7.0 <2.9.0

## Details
Airflow versions 2.7.0 through 2.8.4 have a vulnerability that allows an authenticated user to see sensitive provider configuration via the "configuration" UI page when "non-sensitive-only" was set as "webserver.expose_config" configuration (The celery provider is the only community provider currently that has sensitive configurations). You should migrate to Airflow 2.9 or change your "expose_config" configuration to False as a workaround. This is similar, but different to  CVE-2023-46288 https://github.com/advisories/GHSA-9qqg-mh7c-chfq  which concerned API, not UI configuration page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31869
- https://github.com/apache/airflow/pull/38795
- https://github.com/apache/airflow/commit/042c2acaed7c01933d37c2f8434640ce140a4b27
- https://github.com/apache/airflow
- https://lists.apache.org/thread/pz6vg7wcjk901rmsgt86h76g6kfcgtk3
- http://www.openwall.com/lists/oss-security/2024/04/17/10
