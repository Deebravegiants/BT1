# [M] ALPINE-CVE-2026-56113

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56113
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56113
Type: osv

## Affected
- Alpine:v3.23: `dhcpcd` — affected >=0 <10.5.2-r0
- Alpine:v3.24: `dhcpcd` — affected >=0 <10.5.2-r0

## Details
dhcpcd through 10.3.2, fixed in commit 5733d3c, contains a heap use-after-free vulnerability that allows unauthenticated same-link attackers to crash the daemon by sending a crafted DHCPv6 RENEW reply with RFC6603 OPTION_PD_EXCLUDE and both preferred and valid lifetimes set to zero. Attackers acting as or impersonating a DHCPv6 server can trigger dhcp6_deprecatedele() to free a delegated child address while an outer TAILQ_FOREACH_SAFE iterator in dhcp6_deprecateaddrs() still holds the freed pointer, causing a use-after-free when TAILQ_REMOVE is reached.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56113
