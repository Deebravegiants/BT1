# [H] PolarLearn allows Unauthenticated WebSocket access allows subscribing to and posting in arbitrary group chats

## Summary
Severity: High
Advisory: CVE-2026-25885
Aliases: GHSA-gvjm-5pw7-6c8c
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25885
Type: osv

## Details
PolarLearn is a free and open-source learning program. In 0-PRERELEASE-16 and earlier, the group chat WebSocket at wss://polarlearn.nl/api/v1/ws can be used without logging in. An unauthenticated client can subscribe to any group chat by providing a group UUID, and can also send messages to any group. The server accepts the message and stores it in the group’s chatContent, so this is not just a visual spam issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25885.json
- https://github.com/polarnl/PolarLearn/security/advisories/GHSA-gvjm-5pw7-6c8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25885
- https://github.com/polarnl/PolarLearn/commit/3ba588fda0d3f8e238483a20772719f27e52e79f
