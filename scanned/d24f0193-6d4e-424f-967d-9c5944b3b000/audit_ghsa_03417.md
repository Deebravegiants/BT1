# [H] Incorrect Session Validation in Apache Airflow

## Summary
Severity: High
Advisory: GHSA-7mx5-x372-xh87
CVE: CVE-2020-17526
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-7mx5-x372-xh87
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.14

## Details
Incorrect Session Validation in Apache Airflow Webserver versions prior to 1.10.14 with default config allows a malicious airflow user on site A where they log in normally, to access unauthorized Airflow Webserver on Site B through the session from Site A. This does not affect users who have changed the default value for `[webserver] secret_key` config.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17526
- https://github.com/apache/airflow/commit/2f3b1c780472afd4c8a93633e6633feb7083792e
- https://github.com/apache/airflow/commit/6b065840323f9a4fc8e372b458d26e419e4fa99b
- https://github.com/apache/airflow/commit/97b2735d65e95c4633966667b6db3908540f3937
- https://github.com/apache/airflow/commit/9e01476a50b9be27c4b1e6c6e24d36f290629195
- https://github.com/apache/airflow/commit/a8900fa5f2b8963e9f57ba4ae5520a5d339aeaad
- https://github.com/apache/airflow/commit/dfa7b26ddaca80ee8fd9915ee9f6eac50fac77f6
- https://github.com/apache/airflow/commit/fe6d00a54f83468e296777d3b83b65a2ae7169ec
- https://github.com/advisories/GHSA-7mx5-x372-xh87
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-22.yaml
- https://lists.apache.org/thread.html/r466759f377651f0a690475d5a52564d0e786e82c08d5a5730a4f8352@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rbeeb73a6c741f2f9200d83b9c2220610da314810c4e8c9cf881d47ef%40%3Cusers.airflow.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/12/21/1
