# [H] Apache Airflow: pickle deserialization vulnerability in XComs

## Summary
Severity: High
Advisory: GHSA-c3c6-f2ww-xfr2
CVE: CVE-2023-50943
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-c3c6-f2ww-xfr2
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.8.1rc1

## Details
Apache Airflow, versions before 2.8.1, have a vulnerability that allows a potential attacker to poison the XCom data by bypassing the protection of "enable_xcom_pickling=False" configuration setting resulting in poisoned data after XCom deserialization. This vulnerability is considered low since it requires a DAG author to exploit it. Users are recommended to upgrade to version 2.8.1 or later, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50943
- https://github.com/apache/airflow/pull/36255
- https://github.com/apache/airflow/commit/2c4c5bc604e9ab0cc1e98f7bee7d31d566579462
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-13.yaml
- https://lists.apache.org/thread/fx278v0twqzxkcts70tc04cp3f8p56pn
- http://www.openwall.com/lists/oss-security/2024/01/24/4
