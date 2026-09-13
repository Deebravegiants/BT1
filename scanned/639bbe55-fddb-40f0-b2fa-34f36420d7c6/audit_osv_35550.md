# [M] Use-after-free in Zephyr ICMPv6 RX path when updating statistics after sending an echo reply or error

## Summary
Severity: Medium
Advisory: CVE-2026-10638
Aliases: GHSA-m92g-94xv-wvw2
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-10638
Type: osv

## Details
subsys/net/ip/icmpv6.c reads the network interface from a net_pkt after that packet has been handed to net_try_send_data(). In icmpv6_handle_echo_request() and net_icmpv6_send_error(), the post-send statistics update calls net_pkt_iface(reply)/net_pkt_iface(pkt) on the just-sent packet.

The send path (net_try_send_data -> net_if_tx) unreferences and may free the packet back to its memory slab before returning — synchronously in the RX thread when no TX queue is configured (CONFIG_NET_TC_TX_COUNT == 0), and asynchronously the driver/L2 may already have freed it otherwise. net_pkt_iface() therefore dereferences a freed (and possibly reused) net_pkt; with CONFIG_NET_STATISTICS_PER_INTERFACE the stale iface pointer is further dereferenced and written through (iface->stats.icmp.sent++), turning the use-after-free read into a write through an attacker-influenceable pointer.

The core stack already documents this hazard in net_core.c ("do not use pkt after that call") and caches iface before sending; the ICMPv6 callers did not.

An unauthenticated remote attacker triggers the flaw simply by sending an ICMPv6 Echo Request (ping) or an IPv6 packet that elicits an ICMPv6 error (unknown next header, fragment reassembly timeout, destination unreachable), leading to denial of service via crash and potential memory corruption. Affected: Zephyr networking with CONFIG_NET_NATIVE_IPV6, roughly v4.2.0 through v4.4.0.

The fix caches the interface pointer before sending and uses it for all statistics updates; the sibling commit 86e21665d46 fixes the identical bug in ICMPv4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10638.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-m92g-94xv-wvw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-10638
- https://github.com/zephyrproject-rtos/zephyr/commit/09c8578c66b517c5165cde53332ed5d8d8ef2cfc
- https://github.com/zephyrproject-rtos/zephyr
