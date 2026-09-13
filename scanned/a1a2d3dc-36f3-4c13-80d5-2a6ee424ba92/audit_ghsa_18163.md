# [M] Apache Airflow: Connection sensitive details exposed to users with READ permissions

## Summary
Severity: Medium
Advisory: GHSA-q475-2pgm-7hvp
CVE: CVE-2025-54831
CWE: CWE-213
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-q475-2pgm-7hvp
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.3 <3.0.4

## Details
Apache Airflow 3 introduced a change to the handling of sensitive information in Connections. The intent was to restrict access to sensitive connection fields to Connection Editing Users, effectively applying a "write-only" model for sensitive values.

In Airflow 3.0.3, this model was unintentionally violated: sensitive connection information could be viewed by users with READ permissions through both the API and the UI. This behavior also bypassed the `AIRFLOW__CORE__HIDE_SENSITIVE_VAR_CONN_FIELDS` configuration option.

This issue does not affect Airflow 2.x, where exposing sensitive information to connection editors was the intended and documented behavior.

Users of Airflow 3.0.3 are advised to upgrade Airflow to >=3.0.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54831
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2025-85.yaml
- https://lists.apache.org/thread/vblmfqtydrp5zgn2q8tj3slk5podxspf
- http://www.openwall.com/lists/oss-security/2025/09/25/4
