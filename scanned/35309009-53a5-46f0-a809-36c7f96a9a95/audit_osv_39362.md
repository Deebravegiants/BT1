# [H] DataEase Data Dashboard SqlVariable transFilter Unfiltered SQL Injection

## Summary
Severity: High
Advisory: CVE-2026-45320
Aliases: GHSA-8vp9-9hx4-6458
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-45320
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase dashboard SQL variables such as ${deptId} are processed by SqlparserUtils.transFilter(), whose final branch returns raw user input for non-in and non-between operators before SubstitutedSql.replace("${var}", value) splices it into dashboard SQL, allowing authenticated users who can view a dashboard to inject SQL against integrated datasources. This issue is fixed in version 2.10.23

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45320.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8vp9-9hx4-6458
- https://nvd.nist.gov/vuln/detail/CVE-2026-45320
- https://github.com/dataease/dataease/commit/163d510c6935a4010727392f5a680a7dc15abb13
