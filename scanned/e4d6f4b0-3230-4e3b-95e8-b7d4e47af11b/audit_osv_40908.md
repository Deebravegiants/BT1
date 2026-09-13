# [M] dhcpcd Memory Leak DoS via IPv6 Router Advertisement Handling

## Summary
Severity: Medium
Advisory: CVE-2026-56116
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56116
Type: osv

## Details
dhcpcd through 10.3.2, fixed in commit 708b4a5, contains a memory leak vulnerability in the IPv6 Router Advertisement route information handling that allows an unauthenticated same-link attacker to cause denial of service by sending crafted Router Advertisements. Attackers can repeatedly send Router Advertisements containing Route Information options with a lifetime of zero, triggering unfreed allocations in routeinfo_findalloc() that cause linear memory exhaustion and eventual daemon crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56116
- https://www.vulncheck.com/advisories/dhcpcd-memory-leak-dos-via-ipv6-router-advertisement-handling
- https://github.com/NetworkConfiguration/dhcpcd/commit/708b4a56bae080a5b18c2e0c4c6fbe103131a2b0
- https://github.com/NetworkConfiguration/dhcpcd
