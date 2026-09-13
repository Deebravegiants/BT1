# [H] FlaskBB Authorization Bypass via Topic ID Manipulation

## Summary
Severity: High
Advisory: CVE-2026-22659
Aliases: GHSA-9rjj-9p2h-6c55
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-22659
Type: osv

## Details
FlaskBB through 2.2.0, fixed in commit acc88cf, contains an authorization bypass vulnerability that allows authenticated moderators to perform unauthorized actions on topics in forums they do not control by submitting crafted topic ID lists. Attackers can include a low-ID topic from a permitted forum as an anchor in a batch request, causing the permission check applied only to the first result to pass, and then execute lock, unlock, delete, or hide actions against topics in unmoderated forums.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22659.json
- https://github.com/flaskbb/flaskbb/security/advisories/GHSA-9rjj-9p2h-6c55
- https://nvd.nist.gov/vuln/detail/CVE-2026-22659
- https://www.vulncheck.com/advisories/flaskbb-authorization-bypass-via-topic-id-manipulation
- https://github.com/flaskbb/flaskbb/commit/acc88cfedd011124395e0101cb27432a47f712be
- https://github.com/flaskbb/flaskbb
