# [M] OpenEMR Messages "Show All" Not Restricted to Admins

## Summary
Severity: Medium
Advisory: CVE-2026-25220
Aliases: GHSA-phcp-7qjx-83cm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25220
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the Message Center accepts the URL parameter `show_all=yes` and passes it to `getPnotesByUser()`, which returns all internal messages (all users’ notes). The backend does not verify that the requesting user is an administrator before honoring `show_all=yes`. The "Show All" link is also visible to non-admin users. As a result, any authenticated user can view the entire internal message list by requesting `messages.php?show_all=yes`. Version 8.0.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25220.json
- https://github.com/openemr/openemr/security/advisories/GHSA-phcp-7qjx-83cm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25220
- https://github.com/openemr/openemr/commit/9f2c44fc88fc051fcf0b6922c373977543e6b2af
