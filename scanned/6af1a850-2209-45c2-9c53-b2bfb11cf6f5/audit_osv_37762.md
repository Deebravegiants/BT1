# [M] socket.io allows an unbounded number of binary attachments

## Summary
Severity: Medium
Advisory: CVE-2026-33151
Aliases: GHSA-677m-j7p3-52f9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33151
Type: osv

## Details
Socket.IO is an open source, real-time, bidirectional, event-based, communication framework. Prior to versions 3.3.5, 3.4.4, and 4.2.6, a specially crafted Socket.IO packet can make the server wait for a large number of binary attachments and buffer them, which can be exploited to make the server run out of memory. This issue has been patched in versions 3.3.5, 3.4.4, and 4.2.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33151.json
- https://github.com/socketio/socket.io/security/advisories/GHSA-677m-j7p3-52f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33151
- https://github.com/socketio/socket.io/commit/719f9ebab0772ffb882bd614b387e585c1aa75d4
- https://github.com/socketio/socket.io/commit/9d39f1f080510f036782f2177fac701cc041faaf
- https://github.com/socketio/socket.io/commit/b25738c416c4e32fbff62ee182afa8f6d0dacf78
