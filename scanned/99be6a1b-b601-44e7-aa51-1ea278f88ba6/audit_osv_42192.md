# [C] Onlook tRPC Insecure Direct Object Reference via multiple procedures

## Summary
Severity: Critical
Advisory: CVE-2026-65013
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-65013
Type: osv

## Details
Onlook through 0.2.32, fixed in commit 423e2e9, contains a broken object level authorization vulnerability that allows authenticated attackers to access and manipulate other users' resources by supplying arbitrary UUID values to tRPC API procedures including project.get, member.remove, and chat.conversation.delete. Attackers can provide arbitrary projectId or conversationId values without authorization validation to read, modify, and delete other users' project data, members, and conversation history.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65013.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65013
- https://www.vulncheck.com/advisories/onlook-trpc-insecure-direct-object-reference-via-multiple-procedures
- https://github.com/onlook-dev/onlook/issues/3122
- https://github.com/onlook-dev/onlook/commit/423e2e924366419e418ee049093872d535eea41a
- https://github.com/onlook-dev/onlook/pull/3129
- https://github.com/onlook-dev/onlook
