# [M] Apache Airflow: Bulk JSON Variables bypass should_hide_value_for_key - redact() called without the key

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-48828
Aliases: CVE-2026-48828, GHSA-563f-2439-rmq4, PYSEC-2026-3806
Ecosystem: Bitnami
Published: 2026-07-09
Source: https://osv.dev/vulnerability/BIT-airflow-2026-48828
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.0

## Details
The Bulk Variables API in Apache Airflow called the redactor without passing the variable's key, so the key-based `should_hide_value_for_key` check (which triggers on secret-suffixed key names like `*_password` / `*_token` / `*_secret`) could not fire for JSON-decodable variable values. An authenticated UI/API user with bulk Variable read permission could retrieve plaintext values from JSON variables whose key would otherwise trigger redaction. Affects deployments that store sensitive values in JSON-typed Airflow Variables under secret-suffixed key names. Users are advised to upgrade to `apache-airflow` 3.3.0 or later (the fix landed on `main` after 3.2.2; no 3.2.x backport).

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/2
- https://github.com/apache/airflow/pull/67495
- https://lists.apache.org/thread/y9kf314t6dhnv994hr11wj3tbow847yc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48828
