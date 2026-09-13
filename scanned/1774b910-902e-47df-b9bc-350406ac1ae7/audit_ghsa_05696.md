# [H] Apache Airflow secrets in rendered templates could contain parts of sensitive values when truncated

## Summary
Severity: High
Advisory: GHSA-3qmm-r55x-hpxx
CVE: CVE-2025-68438
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-3qmm-r55x-hpxx
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.1.0 <3.1.6

## Details
In Apache Airflow versions before 3.1.6, when rendered template fields in a Dag exceed [core] max_templated_field_length, sensitive values could be exposed in cleartext in the Rendered Templates UI. This occurred because serialization of those fields used a secrets masker instance that did not include user-registered mask_secret() patterns, so secrets were not reliably masked before truncation and display.

Users are recommended to upgrade to 3.1.6 or later, which fixes this issue

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68438
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-9.yaml
- https://lists.apache.org/thread/55n7b4nlsz3vo5n4h5lrj9bfsk8ctyff
- http://www.openwall.com/lists/oss-security/2026/01/15/5
