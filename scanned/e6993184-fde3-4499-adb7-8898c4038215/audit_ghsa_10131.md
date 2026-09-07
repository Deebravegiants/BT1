# [M] Apache Airlfow: Sensitive Azure Service Bus connection string (and possibly other providers) exposed to users with view access

## Summary
Severity: Medium
Advisory: GHSA-4g48-54q2-fg7q
CVE: CVE-2026-25219
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-4g48-54q2-fg7q
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.1.8

## Details
The `access_key` and `connection_string` connection properties were not marked as sensitive names in secrets masker. This means that user with read permission could see the values in Connection UI, as well as when Connection was accidently logged to logs, those values could be seen in the logs. Azure Service Bus used those properties to store sensitive values. Possibly other providers could be also affected if they used the same fields to store sensitive data.

If you used Azure Service Bus connection with those values set or if you have other connections with those values storing senesitve values, you should upgrade Airflow to 3.1.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25219
- https://github.com/apache/airflow/pull/61580
- https://github.com/apache/airflow/pull/61582
- https://github.com/apache/airflow
- https://lists.apache.org/thread/t4dlmqkn0njz4chk3g7mdgzb96y4ttqh
- http://www.openwall.com/lists/oss-security/2026/04/15/3
