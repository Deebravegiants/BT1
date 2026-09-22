# [M] Use-after-free reading `net_pkt_iface()` of a sent ICMPv4 echo-reply packet in `icmpv4_handle_echo_request()`

## Summary
Severity: Medium
Advisory: CVE-2026-10639
Aliases: GHSA-qhrf-w466-qmpw
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-10639
Type: osv

## Details
In Zephyr's native IPv4 stack, icmpv4_handle_echo_request() in subsys/net/ip/icmpv4.c builds an echo-reply packet (reply), hands it to net_try_send_data(), and then, on success, calls net_stats_update_icmp_sent(net_pkt_iface(reply)). net_try_send_data() transfers ownership of reply to the TX path (net_if_try_queue_tx -> net_if_tx -> L2/driver send, or the asynchronous net_if_tx_thread), which can unref it to refcount 0 and return the struct net_pkt to its slab (net_pkt_unref -> k_mem_slab_free) before the stats line runs. net_core.c documents this exact contract ('the pkt might contain garbage already ... do not use pkt after that call').

The post-send net_pkt_iface(reply) therefore reads reply->iface out of a freed (and possibly already reallocated) net_pkt, a use-after-free read; with CONFIG_NET_STATISTICS_PER_INTERFACE the stats macro additionally increments a counter through that value, i.e. a dereference/write through a stale or recycled-slot pointer.

The path is reached unauthenticated by any remote host that pings the device (net_icmpv4_input -> net_icmp_call_ipv4_handlers -> icmpv4_handle_echo_request) and is gated on CONFIG_NET_STATISTICS_ICMP. Impact is a probabilistic read of recycled packet memory plus a possible wild-pointer write under a timing race, leading most likely to corrupted interface statistics or a remotely triggerable crash (DoS).

The defect was introduced in 2019 (v1.14) and is present through v4.4.0. The companion change in net_icmpv4_send_error() is not a use-after-free because it reads net_pkt_iface(orig), the caller-owned received packet, which stays alive across the send. The fix caches the interface pointer from the live received packet before sending and uses it for the post-send stats updates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10639.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-qhrf-w466-qmpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-10639
- https://github.com/zephyrproject-rtos/zephyr/commit/86e21665d4641f304dc3895bfb03b8f89db83291
- https://github.com/zephyrproject-rtos/zephyr
