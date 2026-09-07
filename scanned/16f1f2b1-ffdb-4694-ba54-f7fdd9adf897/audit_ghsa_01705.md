# [M] XSS in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-rjvg-q57v-mjjc
CVE: CVE-2019-12398
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-05-06
Source: https://github.com/advisories/GHSA-rjvg-q57v-mjjc
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.5

## Details
In Apache Airflow before 1.10.5 when running with the "classic" UI, a malicious admin user could edit the state of objects in the Airflow metadata database to execute arbitrary javascript on certain page views. The new "RBAC" UI is unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12398
- https://github.com/apache/airflow
- https://github.com/apache/airflow/blob/1.10.5/CHANGELOG.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-162.yaml
- https://lists.apache.org/thread.html/r72487ad6b23d18689896962782f8c93032afe5c72a6bfd23b253352b%40%3Cusers.airflow.apache.org%3E
- https://lists.apache.org/thread.html/r72487ad6b23d18689896962782f8c93032afe5c72a6bfd23b253352b@%3Cdev.airflow.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/01/14/2
