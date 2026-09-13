# [M] SiYuan before v3.7.3 Information Disclosure via getHeading*Transaction

## Summary
Severity: Medium
Advisory: CVE-2026-68587
Aliases: GHSA-69mh-gvh4-8gp7, GO-2026-6381
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-68587
Type: osv

## Details
SiYuan versions before v3.7.3 contain an information disclosure vulnerability in the getHeadingDeleteTransaction, getHeadingLevelTransaction, and getHeadingInsertTransaction endpoints that return rendered block DOM without publish-access checks. Anonymous readers or publish RoleReader tokens can supply a heading block ID to read full rendered content of publish-disabled documents that should be restricted.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68587.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-69mh-gvh4-8gp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-68587
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-getheading-transaction
