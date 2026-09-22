# [M] 4ga Boards: User Enumeration via Timing Side-Channel in Authentication Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-41418
Aliases: GHSA-8mj9-p99h-jhxp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41418
Type: osv

## Details
4ga Boards is a boards system for realtime project management. Prior to 3.3.5, 4ga Boards is vulnerable to user enumeration via a timing side-channel in the login endpoint (POST /api/access-tokens). When an invalid username/email is provided, the server responds immediately (~17ms average). When a valid username/email is provided with an incorrect password, the server first performs a bcrypt.compareSync() operation (~74ms average) before responding. This ~4.4× timing difference is trivially detectable even over a network — a single request suffices. This vulnerability is fixed in 3.3.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41418.json
- https://github.com/RARgames/4gaBoards/security/advisories/GHSA-8mj9-p99h-jhxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41418
