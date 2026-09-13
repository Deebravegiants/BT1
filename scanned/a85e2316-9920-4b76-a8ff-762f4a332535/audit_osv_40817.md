# [H] DataEase: Authenticated SQL Injection in Chart Quota Filters

## Summary
Severity: High
Advisory: CVE-2026-55635
Aliases: GHSA-p758-rx6v-hc8g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55635
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, chart quota and Y-axis filters embed attacker-controlled filter values directly into generated SQL in Quota2SQLObj.getYWheres() without applying the SQL literal validation and escaping used by other filter paths, allowing an authenticated user who can create or modify chart definitions or submit chart data requests containing quota filters to inject SQL into queries executed against configured datasources. This issue is fixed in version 2.10.24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55635.json
- https://github.com/dataease/dataease/security/advisories/GHSA-p758-rx6v-hc8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-55635
- https://github.com/dataease/dataease/commit/4463e21cb73d3d4bb8af89a0cb71ee403e4b808a
