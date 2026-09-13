# [M] SiYuan before v3.7.3 Authentication Bypass via Content Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-68584
Aliases: GHSA-7j72-f6wg-cxw6, GO-2026-6382
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-68584
Type: osv

## Details
SiYuan versions before v3.7.3 contain an authentication bypass vulnerability in publish mode where content-returning endpoints getHeadingChildrenDOM, getHeading*Transaction, and getBacklinkDoc perform no password check despite protecting the primary getDoc endpoint. Anonymous attackers can retrieve full content of password-protected documents by obtaining internal block IDs from reader-accessible endpoints and calling unprotected content endpoints to bypass the password gate.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68584.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-7j72-f6wg-cxw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-68584
- https://www.vulncheck.com/advisories/siyuan-before-authentication-bypass-via-content-endpoints
