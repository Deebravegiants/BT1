# [H] Apache Airflow: Execution API HITL Endpoints Missing Per-Task Authorization

## Summary
Severity: High
Advisory: GHSA-8x34-9q3v-h7g8
CVE: CVE-2026-30911
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-8x34-9q3v-h7g8
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.1.0 <3.1.8

## Details
Apache Airflow versions 3.1.0 through 3.1.7 missing authorization vulnerability in the Execution API's Human-in-the-Loop (HITL) endpoints that allows any authenticated task instance to read, approve, or reject HITL workflows belonging to any other task instance.


Users are recommended to upgrade to Apache Airflow 3.1.8 or later, which resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30911
- https://github.com/apache/airflow/pull/62886
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-17.yaml
- https://lists.apache.org/thread/1rs2v7fcko2otl6n9ytthcj87cmsgx51
- http://www.openwall.com/lists/oss-security/2026/03/17/2
