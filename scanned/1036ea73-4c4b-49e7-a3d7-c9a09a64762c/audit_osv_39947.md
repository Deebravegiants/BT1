# [H] CVE-2026-48692

## Summary
Severity: High
Advisory: CVE-2026-48692
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48692
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 exposes a gRPC API server on port 50052 with no authentication mechanism. The server is initialized with grpc::InsecureServerCredentials() (src/fastnetmon.cpp line 477) and a source code comment explicitly acknowledges 'Listen on the given address without any authentication mechanism.' None of the RPC methods in src/api.cpp (ExecuteBan, ExecuteUnBan, GetBanlist, GetTotalTrafficCounters, etc.) perform any credential verification. The ExecuteBan and ExecuteUnBan methods trigger security-critical actions: BGP route announcements that can blackhole network traffic, and execution of external notification scripts via popen(). An attacker with local network access can ban arbitrary IP addresses (causing denial of service to legitimate traffic), unban active attacks (disabling DDoS mitigation), and trigger script execution. There is also no role-based access control separating read-only monitoring from destructive administrative operations.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/api.cpp
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/fastnetmon.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48692
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48692-grpc-no-auth
