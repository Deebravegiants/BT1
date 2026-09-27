# [M] ToolJet is vulnerable to Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-hgp8-w8fj-r4cm
CVE: CVE-2022-4111
CWE: CWE-1284, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-hgp8-w8fj-r4cm
Type: github-advisory

## Affected
- npm: `tooljet` — affected >=0 <1.27.0

## Details
ToolJet/ToolJet placed no limit on the file size for user avatars. This could cause a denial of service if too many users upload large files. This is fixed in commit 01cd3f0464747973ec329e9fb1ea12743d3235cc in version 1.27.0.

`tooljet` is no longer listed on npmjs.com but was [listed on npmjs.com in the past](https://web.archive.org/web/20220210014826/https://www.npmjs.com/package/tooljet). This advisory is maintained for historical completeness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4111
- https://github.com/ToolJet/ToolJet/pull/4103
- https://github.com/tooljet/tooljet/commit/01cd3f0464747973ec329e9fb1ea12743d3235cc
- https://github.com/ToolJet/ToolJet
- https://huntr.dev/bounties/5596d072-66d2-4361-8cac-101c9c781c3d
