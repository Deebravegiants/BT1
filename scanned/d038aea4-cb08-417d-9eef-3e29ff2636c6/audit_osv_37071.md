# [M] Firebird server hangs when using specific clumplet on batch creation

## Summary
Severity: Medium
Advisory: CVE-2026-28214
Aliases: GHSA-7cq5-994r-jhrf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-28214
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, the ClumpletReader::getClumpletSize() function can overflow the totalLength value when parsing a Wide type clumplet, causing an infinite loop. An authenticated user with INSERT privileges on any table can exploit this via a crafted Batch Parameter Block to cause a denial of service against the server. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28214.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-7cq5-994r-jhrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28214
