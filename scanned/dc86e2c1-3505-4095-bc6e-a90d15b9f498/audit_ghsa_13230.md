# [H] Apache HDFS Provider error message suggested

## Summary
Severity: High
Advisory: GHSA-5hj9-m76g-xrc8
CVE: CVE-2023-41267
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-14
Source: https://github.com/advisories/GHSA-5hj9-m76g-xrc8
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-hdfs` — affected >=0 <4.1.1

## Details
In the Apache Airflow HDFS Provider, versions prior to 4.1.1, a documentation info pointed users to an install incorrect pip package. As this package name was unclaimed, in theory, an attacker could claim this package and provide code that would be executed when this package was installed. The Airflow team has since taken ownership of the package (neutralizing the risk), and fixed the doc strings in version 4.1.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41267
- https://github.com/apache/airflow/pull/33813
- https://github.com/apache/airflow
- https://lists.apache.org/thread/ggthr5pn42bn6wcr25hxnykjzh4ntw7z
- http://www.openwall.com/lists/oss-security/2023/09/14/3
