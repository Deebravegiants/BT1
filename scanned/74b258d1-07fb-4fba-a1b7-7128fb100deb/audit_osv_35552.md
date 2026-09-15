# [M] Use-after-free reading `net_pkt` `iface` after send in IPv6 Neighbor Discovery (`ipv6_nbr.c`)

## Summary
Severity: Medium
Advisory: CVE-2026-10640
Aliases: GHSA-r74c-mr4m-7g9g
CVSS: 4.2 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-10640
Type: osv

## Details
Zephyr's IPv6 Neighbor Discovery send paths (net_ipv6_send_na, net_ipv6_send_ns, net_ipv6_send_rs in subsys/net/ip/ipv6_nbr.c) updated the per-interface ICMP-sent statistics by calling net_pkt_iface(pkt) after net_send_data(pkt) had already returned successfully. On the success path the network stack owns and releases the packet's reference (the L2/driver send unrefs it, e.g. ethernet_send -> net_pkt_unref), so for a freshly allocated packet with refcount 1 the net_pkt slab block can be freed before the statistics line runs (synchronously when no TX queue thread is configured, or via a concurrent TX thread otherwise).

The subsequent net_pkt_iface(pkt) reads pkt->iface from the freed slab block, and with CONFIG_NET_STATISTICS_PER_INTERFACE enabled that loaded pointer is dereferenced to increment iface->stats.icmp.sent, a use-after-free (CWE-416). If the slab block was reallocated in the meantime the read/increment targets unrelated or attacker-influenced memory, yielding corrupted statistics, a fault/crash (denial of service), or potential limited memory corruption.

The vulnerable Neighbor Advertisement path is reachable by any unauthenticated on-link node simply by sending ICMPv6 Neighbor Solicitations to a Zephyr node with native IPv6 enabled (handle_ns_input -> net_ipv6_send_na).

Affected from v3.3.0 through v4.4.0; the fix uses the already-available iface argument instead of touching the sent packet. Configurations without per-interface statistics dereference only a global counter and are not affected by the memory-safety aspect.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10640.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-r74c-mr4m-7g9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-10640
- https://github.com/zephyrproject-rtos/zephyr/commit/aaed8332a62b0490a2f3c2cbabe272f575068eaa
- https://github.com/zephyrproject-rtos/zephyr
