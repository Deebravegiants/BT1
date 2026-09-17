# [H] DataEase has SQL Injection via Datasource Management

## Summary
Severity: High
Advisory: CVE-2026-33122
Aliases: GHSA-28vg-3hv7-w92f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33122
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below contain a SQL injection vulnerability in the API datasource update process. When a new table definition is added during a datasource update via /de2api/datasource/update, the deTableName field from the user-submitted configuration is passed to DatasourceSyncManage.createEngineTable, where it is substituted into a CREATE TABLE statement template without any sanitization or identifier escaping. An authenticated attacker can inject arbitrary SQL commands by crafting a deTableName that breaks out of identifier quoting, enabling error-based SQL injection that can extract database information. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33122.json
- https://github.com/dataease/dataease/security/advisories/GHSA-28vg-3hv7-w92f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33122
