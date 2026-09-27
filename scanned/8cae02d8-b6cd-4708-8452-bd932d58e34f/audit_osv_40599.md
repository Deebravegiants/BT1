# [H] DataEase: Unauthorized Access to Engine Database via previewSql Endpoint

## Summary
Severity: High
Advisory: CVE-2026-53730
Aliases: GHSA-2jmq-vffm-4qmj
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-53730
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, the /de2api/datasetData/previewSql endpoint lacks the mandatory @DePermit permission validation annotation, allowing any authenticated user to specify datasourceId=-1, access the built-in engine database, execute arbitrary SQL statements, and read sensitive core data. This issue is fixed in version 2.10.24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53730.json
- https://github.com/dataease/dataease/security/advisories/GHSA-2jmq-vffm-4qmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-53730
- https://github.com/dataease/dataease/commit/7b47af38b8fa017c9eecb00a4a49264663189e7b
