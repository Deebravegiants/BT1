# [H] Apache Airflow subject to Exposure of Sensitive Information

## Summary
Severity: High
Advisory: GHSA-fvw2-2pf7-77vw
CVE: CVE-2022-27949
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-14
Source: https://github.com/advisories/GHSA-fvw2-2pf7-77vw
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.3.1

## Details
A vulnerability in UI of Apache Airflow allows an attacker to view unmasked secrets in rendered template values for tasks which were not executed (for example when they were depending on past and previous instances of the task failed). This issue affects Apache Airflow prior to 2.3.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27949
- https://github.com/apache/airflow/pull/22754
- https://github.com/apache/airflow/commit/09be0c5c7e847dda1d0be5776f8d5e327ff2281a
- https://github.com/apache/airflow/commit/1cbb0ad26dd17f218c6ab1c2ae59b262c443a443
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2022-42981.yaml
- https://lists.apache.org/thread/n38oc5obb48600fsvnbopxcs0jpbp65p
- http://www.openwall.com/lists/oss-security/2022/11/14/3
