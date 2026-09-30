# [H] Apache Airflow vulnerable to exposure of sensitive information

## Summary
Severity: High
Advisory: GHSA-mjff-wv85-hmcj
CVE: CVE-2023-35005
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-mjff-wv85-hmcj
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.5.0 <2.6.2rc1

## Details
In Apache Airflow, some potentially sensitive values were being shown to the user in certain situations.

This vulnerability is mitigated by the fact configuration is not shown in the UI by default (only if `[webserver] expose_config` is set to `non-sensitive-only`), and not all uncensored values are actually sentitive.

This issue affects Apache Airflow: from 2.5.0 before 2.6.2. Users are recommended to update to version 2.6.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35005
- https://github.com/apache/airflow/pull/31788
- https://github.com/apache/airflow/pull/31820
- https://github.com/apache/airflow/commit/5679a01919ac9d5153e858f8b1390cbc7915f148
- https://github.com/apache/airflow/commit/f6cda8fb63250fc4700658999739c1c3c5f6625c
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-89.yaml
- https://lists.apache.org/thread/o4f2cxh0054m9tlxpb81c1yhylor5gjd
