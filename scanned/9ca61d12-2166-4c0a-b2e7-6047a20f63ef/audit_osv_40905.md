# [M] dhcpcd Heap Use-After-Free in dhcp6_deprecateaddrs via DHCPv6 RENEW

## Summary
Severity: Medium
Advisory: CVE-2026-56113
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56113
Type: osv

## Details
dhcpcd through 10.3.2, fixed in commit 5733d3c, contains a heap use-after-free vulnerability that allows unauthenticated same-link attackers to crash the daemon by sending a crafted DHCPv6 RENEW reply with RFC6603 OPTION_PD_EXCLUDE and both preferred and valid lifetimes set to zero. Attackers acting as or impersonating a DHCPv6 server can trigger dhcp6_deprecatedele() to free a delegated child address while an outer TAILQ_FOREACH_SAFE iterator in dhcp6_deprecateaddrs() still holds the freed pointer, causing a use-after-free when TAILQ_REMOVE is reached.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56113
- https://www.vulncheck.com/advisories/dhcpcd-heap-use-after-free-in-dhcp6-deprecateaddrs-via-dhcpv6-renew
- https://github.com/NetworkConfiguration/dhcpcd/commit/5733d3c59a5651f64357ac11c98b4f39895c8d25
- https://github.com/NetworkConfiguration/dhcpcd
