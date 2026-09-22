# [H] Apache Airflow has a Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-wr76-29cr-67w8
CVE: CVE-2026-42359
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-wr76-29cr-67w8
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.2.0 <3.2.2

## Details
A bug in Apache Airflow's XCom PATCH endpoint `PATCH /api/v2/xcomEntries/{key}` allowed an authenticated UI/API user with XCom write permission on a Dag to set XCom entries under reserved key names (e.g. `return_value`) that the matching POST endpoint already validated against `FORBIDDEN_XCOM_KEYS`. The endpoint also accepted serialized payload shapes the triggerer's deserializer treats as code; combined, this allowed RCE on the triggerer when the affected task next deferred. Affects deployments where untrusted users have XCom write permission on Dags that defer to the triggerer. This is a fix-bypass of CVE-2026-33858: PR #64148 added the `FORBIDDEN_XCOM_KEYS` validator only on the POST/set path; the PATCH path was not covered. Users who already upgraded for CVE-2026-33858 should additionally upgrade to `apache-airflow` 3.2.2 or later to cover the PATCH-path bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42359
- https://github.com/apache/airflow/pull/65915
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-185.yaml
- https://lists.apache.org/thread/g8dqykpf1p90tysq8tln4qtkqwb1038s
- https://www.cve.org/CVERecord?id=CVE-2026-33858
