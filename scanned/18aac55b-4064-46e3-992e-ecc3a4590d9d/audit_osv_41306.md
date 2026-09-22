# [M] AFFiNE - Unauthorized Document Edit History Access via GraphQL histories Field

## Summary
Severity: Medium
Advisory: CVE-2026-59262
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59262
Type: osv

## Details
AFFiNE's histories GraphQL field fails to validate Doc.Read permission before exposing document edit history, allowing authenticated workspace members to retrieve restricted content timelines. Attackers can supply arbitrary document GUIDs to access full edit histories including user names, emails, and timestamps of private pages they lack access to.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59262
- https://www.vulncheck.com/advisories/affine-unauthorized-document-edit-history-access-via-graphql-histories-field
- https://github.com/toeverything/AFFiNE/issues/15179
- https://github.com/toeverything/AFFiNE/commit/1f0bcd01a37a522393fc1b288395e3a72a79ccad
- https://github.com/toeverything/AFFiNE
