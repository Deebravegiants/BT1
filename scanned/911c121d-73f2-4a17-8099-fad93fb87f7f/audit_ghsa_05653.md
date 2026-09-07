# [H] Apache Airflow proxy credentials for various providers might leak in task logs

## Summary
Severity: High
Advisory: GHSA-7c2f-r6gc-h92h
CVE: CVE-2025-68675
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-7c2f-r6gc-h92h
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0b1 <3.1.6
- PyPI: `apache-airflow` — affected >=0 <2.11.1

## Details
In Apache Airflow versions before 3.1.6, and 2.11.1 the proxies and proxy fields within a Connection may include proxy URLs containing embedded authentication information. These fields were not treated as sensitive by default and therefore were not automatically masked in log output. As a result, when such connections are rendered or printed to logs, proxy credentials embedded in these fields could be exposed.

Users are recommended to upgrade to 3.1.6 or later for Airflow 3, and 2.11.1 or later for Airflow 2 which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68675
- https://github.com/apache/airflow/pull/59688
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-10.yaml
- https://lists.apache.org/thread/x6kply4nqd4vc4wgxtm6g9r2tt63s8c5
- http://www.openwall.com/lists/oss-security/2026/01/15/6
