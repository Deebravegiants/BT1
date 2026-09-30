# [M] Apache Airflow: Sensitive parameters exposed in API when "non-sensitive-only" configuration is set

## Summary
Severity: Medium
Advisory: BIT-airflow-2023-46288
Aliases: CVE-2023-46288, GHSA-9qqg-mh7c-chfq, PYSEC-2023-218
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2023-46288
Type: osv

## Affected
- Bitnami: `airflow` — affected >=2.4.0 <2.7.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Airflow.This issue affects Apache Airflow from 2.4.0 to 2.7.0.

Sensitive configuration information has been exposed to authenticated users with the ability to read configuration via Airflow REST API for configuration even when the expose_config option is set to non-sensitive-only. The expose_config option is False by default. It is recommended to upgrade to a version that is not affected if you set expose_config to non-sensitive-only configuration. This is a different error than CVE-2023-45348 which allows authenticated user to retrieve individual configuration values in 2.7.* by specially crafting their request (solved in 2.7.2).

Users are recommended to upgrade to version 2.7.2, which fixes the issue and additionally fixes CVE-2023-45348.

## References
- https://github.com/apache/airflow/pull/32261
- https://lists.apache.org/thread/yw4vzm0c5lqkwm0bxv6qy03yfd1od4nw
- http://www.openwall.com/lists/oss-security/2024/04/17/10
- https://nvd.nist.gov/vuln/detail/CVE-2023-46288
