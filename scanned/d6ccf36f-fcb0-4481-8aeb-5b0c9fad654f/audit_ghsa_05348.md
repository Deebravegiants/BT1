# [H] Apache Airflow Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-2r5m-76wx-56gx
CVE: CVE-2026-45360
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-2r5m-76wx-56gx
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.2.0 <3.2.2

## Details
Apache Airflow's scheduler-side deadline-reference decoder (`SerializedCustomReference.deserialize_reference`) imported and dispatched arbitrary class paths drawn from DAG-author-controlled serialized state without an allowlist or plugin-registry gate. A DAG author whose code reaches the scheduler — the default on single-host deployments where the DAG bundle is importable from the scheduler process — could embed a custom `DeadlineReference` whose serialized form named an attacker-controlled module path, causing the scheduler to `import_string(...)` and instantiate that class with a live SQLAlchemy session attached. Affects deployments where DAG-author code is less trusted than the scheduler process. Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45360
- https://github.com/apache/airflow/pull/61461
- https://github.com/apache/airflow/pull/66737
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-186.yaml
- https://lists.apache.org/thread/q227dghjwgfz8xsxrf2pwpz4wk43zm83
- http://www.openwall.com/lists/oss-security/2026/05/31/12
