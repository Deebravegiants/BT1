# [H] Apache Airflow: Unsafe Deserialization via Legacy Serialization Keys (__type/__var) Bypass in XCom API

## Summary
Severity: High
Advisory: GHSA-mc4f-r875-v87w
CVE: CVE-2026-33858
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-mc4f-r875-v87w
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.1.8 <3.2.0

## Details
Dag Authors, who normally should not be able to execute code in the webserver context could craft XCom payload causing the webserver to execute arbitrary code. Since Dag Authors are already highly trusted, severity of this issue is Low.


Users are recommended to upgrade to Apache Airflow 3.2.0, which resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33858
- https://github.com/apache/airflow/pull/64148
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-20.yaml
- https://lists.apache.org/thread/1npt3o2x81s0gw9tmfcv4n7p1z9hdmy0
- http://www.openwall.com/lists/oss-security/2026/04/13/7
