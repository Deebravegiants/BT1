# [C] Improper Certificate Validation in apache airflow mongo hook

## Summary
Severity: Critical
Advisory: GHSA-x5pm-h33q-cjrw
CVE: CVE-2024-25141
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-x5pm-h33q-cjrw
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-mongo` — affected >=0 <4.0.0

## Details
When ssl was enabled for Mongo Hook, default settings included "allow_insecure" which caused that certificates were not validated. This was unexpected and undocumented.
Users are recommended to upgrade to version 4.0.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25141
- https://github.com/apache/airflow/pull/37214
- https://github.com/apache/airflow
- https://lists.apache.org/thread/sqgbfqngjmn45ommmrgj7hvs7fgspsgm
- http://www.openwall.com/lists/oss-security/2024/02/20/5
