# [M] Apache Airflow: Incomplete redaction allowlist exposes secrets in Connection `extra`  to read-permitted users

## Summary
Severity: Medium
Advisory: GHSA-2883-wwh7-x57v
CVE: CVE-2026-45192
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-2883-wwh7-x57v
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.2

## Details
A bug in the GET `/api/v2/connections/{connection_id}` REST API endpoint in Apache Airflow allowed an authenticated UI/API user with Connection-read permission to retrieve secrets stored in a Connection's `extra` JSON blob under field names not present in the redaction allowlist (`DEFAULT_SENSITIVE_FIELDS`) — for example, official Slack-provider credential field names were returned in plaintext. Affects deployments that store credentials in Connection `extra` blobs and grant Connection-read access to multiple users. Users are advised to upgrade to `apache-airflow` 3.2.2 or later. As a defense-in-depth mitigation, deployment operators can store sensitive credential values in a secret-backend rather than inlined into the Connection's `extra` field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45192
- https://github.com/apache/airflow/pull/66673
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-173.yaml
- https://lists.apache.org/thread/r2q93dg2wp5h9sd9vh6y4y5ljqd9crdd
- http://www.openwall.com/lists/oss-security/2026/06/01/3
