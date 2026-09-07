# [H] Netty has an IPv6 Subnet Filter Bypass via Incorrect Comparator Masking

## Summary
Severity: High
Advisory: GHSA-3qp7-7mw8-wx86
CVE: CVE-2026-44249
CWE: CWE-284, CWE-697
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-3qp7-7mw8-wx86
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-handler` — affected >=0 <4.1.135.Final

## Details
### Summary
An attacker can bypass IPv6 subnet rules due to an incorrect masking operation in IpSubnetFilterRule.compareTo(). Valid public IP addresses can bypass the restrictions.

### Details
`io.netty.handler.ipfilter.IpSubnetFilterRule#compareTo(java.net.InetSocketAddress)` method performs a bitwise AND between the incoming IP address and the configured networkAddress, instead of the subnetMask.

### Impact
Access Control Bypass. Attacker can bypass IpSubnetFilter IPv6 access controls.

## References
- https://github.com/netty/netty/security/advisories/GHSA-3qp7-7mw8-wx86
- https://nvd.nist.gov/vuln/detail/CVE-2026-44249
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
