# [H] Apache Airflow Spark Provider Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-r2f6-6928-fh8f
CVE: CVE-2023-40272
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-17
Source: https://github.com/advisories/GHSA-r2f6-6928-fh8f
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-spark` — affected >=0 <4.1.3

## Details
Apache Airflow Spark Provider, versions before 4.1.3, is affected by a vulnerability that allows an attacker to pass in malicious parameters when establishing a connection giving an opportunity to read files on the Airflow server.
It is recommended to upgrade to a version that is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40272
- https://lists.apache.org/thread/t03gktyzyor20rh06okd91jtqmw6k1l7
- http://www.openwall.com/lists/oss-security/2023/08/17/1
- http://www.openwall.com/lists/oss-security/2023/08/18/1
