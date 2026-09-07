# [H] Apache Airflow allows code execution through crafted XCom payloads

## Summary
Severity: High
Advisory: GHSA-6ffj-2wg2-w45j
CVE: CVE-2026-25917
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-6ffj-2wg2-w45j
Type: github-advisory

## Affected
- PyPI: `apache-airflow-core` — affected >=0 <3.2.0

## Details
Dag Authors, who normally should not be able to execute code in the webserver context could craft XCom payload causing the webserver to execute arbitrary code. Since Dag Authors are already highly trusted, severity of this issue is Low. Users are recommended to upgrade to Apache Airflow 3.2.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25917
- https://github.com/apache/airflow/pull/61641
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-13.yaml
- https://lists.apache.org/thread/6whgpkqbh12rvpfmvcg8b0vwlv4hq3po
- http://www.openwall.com/lists/oss-security/2026/04/17/9
