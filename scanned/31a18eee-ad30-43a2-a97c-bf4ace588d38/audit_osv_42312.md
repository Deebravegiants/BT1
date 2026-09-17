# [M] Let's Chat 0.4.0 - 0.4.8 Denial of Service via Null Dereference in Room Lookup

## Summary
Severity: Medium
Advisory: CVE-2026-66749
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-66749
Type: osv

## Details
Let's Chat 0.4.0 through 0.4.8 contains a null dereference vulnerability that allows authenticated attackers to crash the server by supplying a valid 24-character hex string room parameter that matches no document in the database. Attackers can send a crafted GET /messages request causing an uncaught TypeError in an asynchronous Mongoose callback that terminates the Node.js server process, with the same defect reachable through multiple code paths including the socket.io interface.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66749.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66749
- https://www.vulncheck.com/advisories/let-s-chat-denial-of-service-via-null-dereference-in-room-lookup
- https://github.com/sdelements/lets-chat
- https://github.com/theopaid/Unchecked-Room-Lookup-Leads-to-Server-Crash-Let-s-Chat-
