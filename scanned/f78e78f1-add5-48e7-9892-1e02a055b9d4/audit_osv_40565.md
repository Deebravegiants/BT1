# [H] Termix: Server-Side Request Forgery via Proxy Connectivity Test

## Summary
Severity: High
Advisory: CVE-2026-53549
Aliases: GHSA-x9pr-795g-rm5f
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53549
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to 2.3.2, the POST /host/db/proxy/test endpoint accepts the singleProxy, proxyChain, and testTarget request fields without validating their destination addresses. The testProxyConnectivity path uses raw TCP and SOCKS connections to attacker-selected hosts and ports, allowing an authenticated user to probe localhost, private networks, link-local metadata services, and other infrastructure reachable from the Termix server. Structured connection errors disclose host reachability and timing information, and successful metadata access can expose cloud credentials. This issue is fixed in version 2.3.2.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53549.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-x9pr-795g-rm5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-53549
- https://github.com/Termix-SSH/Termix/commit/52f4e51ae03b5b8d2608e1383e2ccf79d290132b
- https://github.com/Termix-SSH/Termix/pull/874
