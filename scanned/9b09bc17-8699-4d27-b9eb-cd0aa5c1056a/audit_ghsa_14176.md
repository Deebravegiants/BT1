# [C] Apache Airflow Hive Provider vulnerable to code injection

## Summary
Severity: Critical
Advisory: GHSA-5cvg-9pp5-mxcj
CVE: CVE-2023-28706
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-5cvg-9pp5-mxcj
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-hive` — affected >=0 <6.0.0

## Details
Apache Software Foundation's Apache Airflow Hive Provider before 6.0.0 is vulnerable to improper control of generation of code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28706
- https://github.com/apache/airflow/pull/30212
- https://github.com/apache/airflow
- https://lists.apache.org/thread/dl20xxd51xvlx0zzc0wzgxfjwgtbbxo3
- http://www.openwall.com/lists/oss-security/2023/04/07/2
