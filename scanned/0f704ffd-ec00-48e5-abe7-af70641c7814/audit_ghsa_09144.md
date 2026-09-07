# [M] Apache Airflow Providers Elasticsearch: Elasticsearch task-log handlers leak credentials embedded in the host URL

## Summary
Severity: Medium
Advisory: GHSA-g3jr-4jrm-jvqv
CVE: CVE-2026-41018
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-g3jr-4jrm-jvqv
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-elasticsearch` — affected >=0 <6.5.3

## Details
The Elasticsearch logging provider, when configured with a `host` URL that embeds credentials (for example `https://user:password@server.example.com:9200`), wrote the full host URL — including the embedded credentials — into task logs. Any user with task-log read permission could harvest the backend credentials. Users are advised to upgrade to `apache-airflow-providers-elasticsearch` 6.5.3 or later and, as a defense-in-depth measure, configure the backend credentials via a secret backend rather than embedding them in the `[elasticsearch] host` URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41018
- https://github.com/apache/airflow/pull/65349
- https://github.com/apache/airflow/commit/f9244064016a8db45277efb0c24808e663b233f3
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-elasticsearch/PYSEC-2026-22.yaml
- https://lists.apache.org/thread/wz5l58drprmwlv6jxnq466x24jqbbhp7
- http://www.openwall.com/lists/oss-security/2026/05/10/3
