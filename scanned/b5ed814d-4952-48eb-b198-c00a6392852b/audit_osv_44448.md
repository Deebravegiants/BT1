# [C] Shinobi before commit 5a76c74f Arbitrary Database Query Execution via Hardcoded Child Node Key

## Summary
Severity: Critical
Advisory: CVE-2026-82448
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82448
Type: osv

## Details
Shinobi before commit 5a76c74f contains a hardcoded connection key in the child node service that allows unauthenticated attackers to execute arbitrary database queries. Attackers reaching the child node port can present the hardcoded key during WebSocket handshake, then dispatch SQL queries through the onWebSocketDataFromChildNode handler to read and modify user records and camera configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82448
- https://www.vulncheck.com/advisories/shinobi-before-commit-5a76c74f-arbitrary-database-query-execution-via-hardcoded-child-node-key
- https://gitlab.com/Shinobi-Systems/Shinobi/-/merge_requests/554
- https://gitlab.com/Shinobi-Systems/Shinobi/-/commit/5a76c74f3977661ff3f9fd55a260db352c0b19c0
- https://gitlab.com/Shinobi-Systems/Shinobi
- https://gitlab.com/Shinobi-Systems/Shinobi/-/blob/f04e685b8bd4c6190fcd62993131b86a76c2b806/libs/childNode/utils.js
