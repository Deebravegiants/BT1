# [M] Apache Airflow vulnerable to stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-vcf6-3wv2-5vcr
CVE: CVE-2023-29247
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-08
Source: https://github.com/advisories/GHSA-vcf6-3wv2-5vcr
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.6.0

## Details
Task instance details page in the UI is vulnerable to stored cross-site scripting. This issue affects Apache Airflow before 2.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29247
- https://github.com/apache/airflow/pull/30447
- https://github.com/apache/airflow/pull/30779
- https://github.com/apache/airflow/commit/46c85ec11d224c133da6c45c1186c9aa498a7e75
- https://github.com/apache/airflow/commit/f819dfcb24c597058b7b671f6317e4c84976975e
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-60.yaml
- https://lists.apache.org/thread/kqf5lxmko133780clsp827xfsh4xd3fl
