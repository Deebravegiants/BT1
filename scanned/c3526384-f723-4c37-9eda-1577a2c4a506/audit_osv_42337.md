# [M] Perspective 5.0.0 DoS via VirtualServer Protocol Dispatcher

## Summary
Severity: Medium
Advisory: CVE-2026-67198
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-67198
Type: osv

## Details
Perspective 5.0.0 contains a denial-of-service vulnerability in the VirtualServer protocol dispatcher that allows unauthenticated remote attackers to crash the server process by sending malformed or incomplete protobuf messages. Attackers can send well-formed requests such as ViewToArrowReq with no viewport set or MakeTableReq with no data field to trigger unwrap() calls on None values at nine distinct sites, causing the process to abort with SIGABRT.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67198
- https://www.vulncheck.com/advisories/perspective-dos-via-virtualserver-protocol-dispatcher
- https://github.com/perspective-dev/perspective
- https://christbowel.com/blog/perspective-5-0-0-five-cves/
