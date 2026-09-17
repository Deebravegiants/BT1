# [M] Apache Airflow exposes arbitrary file content

## Summary
Severity: Medium
Advisory: GHSA-q8h9-pqcx-59hw
CVE: CVE-2022-38170
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-03
Source: https://github.com/advisories/GHSA-q8h9-pqcx-59hw
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.3.4

## Details
In Apache Airflow prior to 2.3.4, an insecure umask was configured for numerous Airflow components when running with the `--daemon` flag which could result in a race condition giving world-writable files in the Airflow home directory and allowing local users to expose arbitrary file contents via the webserver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38170
- https://github.com/apache/airflow/commit/b6a2cd1aa34f69a36ea127e4f7f5ba87f4aca420
- https://github.com/apache/airflow/commit/bf01d10cd348e679916034de1befb79ec6e46ff8
- https://github.com/apache/airflow/commit/c14ea8f0f34944d2ecfa9021d167602e8b2b8b90
- https://github.com/advisories/GHSA-q8h9-pqcx-59hw
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2022-261.yaml
- https://lists.apache.org/thread/zn8mbbb1j2od5nc9zhrvb7rpsrg1vvzv
- http://www.openwall.com/lists/oss-security/2022/09/02/12
- http://www.openwall.com/lists/oss-security/2022/09/02/3
- http://www.openwall.com/lists/oss-security/2022/09/21/2
