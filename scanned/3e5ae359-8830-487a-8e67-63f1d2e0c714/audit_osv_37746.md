# [C] DataEase has SQL Injection via Datasource Save Flow

## Summary
Severity: Critical
Advisory: CVE-2026-33121
Aliases: GHSA-fg4m-q7ch-jqv5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33121
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below contain a SQL injection vulnerability in the API datasource saving process. The deTableName field from the Base64-encoded datasource configuration is used to construct a DDL statement via simple string replacement without any sanitization or escaping of the table name. An authenticated attacker can inject arbitrary SQL commands by crafting a deTableName that breaks out of identifier quoting, enabling error-based SQL injection that can extract database information such as the MySQL version. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33121.json
- https://github.com/dataease/dataease/security/advisories/GHSA-fg4m-q7ch-jqv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33121
