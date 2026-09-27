# [M] Apache Airflow: Arbitrary airflow.* class instantiation on the API server via the XCom deserialize endpoint

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-59242
Aliases: CVE-2026-59242
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-59242
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's XCom `GET /api/v2/{...}/xcomEntries/{key}?deserialize=true` endpoint passed a string-literal payload through `BaseXCom.deserialize_value` without the `_check_forbidden_xcom_keys` guard, allowing an authenticated API user with XCom write-and-read access to instantiate arbitrary `airflow.*` classes on the API server (CWE-502). An authenticated user who can write an XCom value and then read it back with `deserialize=true` triggers the unsafe instantiation. Users are advised to upgrade to apache-airflow 3.3.1 or later, which rejects reserved XCom serialization keys submitted as JSON string literals.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/6
- https://github.com/apache/airflow/pull/69378
- https://lists.apache.org/thread/dm0520yhh4mn7qknyoh45r2w6c5qg2mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-59242
