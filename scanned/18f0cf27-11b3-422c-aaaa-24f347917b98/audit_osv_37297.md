# [C] OpenWrt Project has a Stack-based Buffer Overflow vulnerability via IPv6 reverse DNS lookup

## Summary
Severity: Critical
Advisory: CVE-2026-30872
Aliases: GHSA-mpgh-v658-jqv5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-30872
Type: osv

## Details
OpenWrt Project is a Linux operating system targeting embedded devices. In versions prior to 24.10.6 and 25.12.1, the mdns daemon has a Stack-based Buffer Overflow vulnerability in the match_ipv6_addresses function, triggered when processing PTR queries for IPv6 reverse DNS domains (.ip6.arpa) received via multicast DNS on UDP port 5353. During processing, the domain name from name_buffer is copied via strcpy into a fixed 256-byte stack buffer, and then the reverse IPv6 request is extracted into a buffer of only 46 bytes (INET6_ADDRSTRLEN). Because the length of the data is never validated before this extraction, an attacker can supply input larger than 46 bytes, causing an out-of-bounds write. This allows a specially crafted DNS query to overflow the stack buffer in match_ipv6_addresses, potentially enabling remote code execution. This issue has been fixed in versions 24.10.6 and 25.12.1.

## References
- https://github.com/openwrt/openwrt/releases/tag/v24.10.6
- https://github.com/openwrt/openwrt/releases/tag/v25.12.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30872.json
- https://github.com/openwrt/openwrt/security/advisories/GHSA-mpgh-v658-jqv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-30872
