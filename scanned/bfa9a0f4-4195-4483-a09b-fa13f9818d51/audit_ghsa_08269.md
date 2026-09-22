# [M] Apache Airflow Providers OpenSearch: OpenSearch task-log handler leaks credentials embedded in the host URL

## Summary
Severity: Medium
Advisory: GHSA-xccp-97wp-3gjg
CVE: CVE-2026-43826
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-xccp-97wp-3gjg
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-opensearch` — affected >=0 <1.9.1

## Details
The OpenSearch logging provider, when configured with a `host` URL that embeds credentials (for example `https://user:password@server.example.com:9200`), wrote the full host URL — including the embedded credentials — into task logs. Any user with task-log read permission could harvest the backend credentials. Users are advised to upgrade to `apache-airflow-providers-opensearch` 1.9.1 or later and, as a defense-in-depth measure, configure the backend credentials via a secret backend rather than embedding them in the `[opensearch] host` URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43826
- https://github.com/apache/airflow/pull/65509
- https://github.com/apache/airflow/commit/6a6b6ff409fb48c28bd63482828632a3c5a5bb93
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-opensearch/PYSEC-2026-23.yaml
- https://lists.apache.org/thread/bxsrqx1vwssovnwnrvgh9xcosptmf73y
- http://www.openwall.com/lists/oss-security/2026/05/10/2
