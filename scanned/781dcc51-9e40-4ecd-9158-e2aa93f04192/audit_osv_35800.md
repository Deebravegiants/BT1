# [M] Ethernet bridge RX packet leak enables denial of service via RX buffer-pool exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-14696
Aliases: GHSA-3m4w-wc4v-766q
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-14696
Type: osv

## Details
When Ethernet bridging is enabled (CONFIG_NET_ETHERNET_BRIDGE), eth_bridge_input_process() in subsys/net/l2/ethernet/bridge/bridge_input.c decides how each frame received on a bridge member interface is handled. For frames that must also be delivered to the local stack, the code called eth_bridge_handle_locally() and returned NET_OK. That helper does not consume the packet — it only calls bridge_iface_recv() (via virtual_recv()), which returns NET_CONTINUE without taking ownership of pkt.

The NET_OK verdict then propagates through ethernet_recv() up to processing_data() in subsys/net/ip/net_core.c, where NET_OK is interpreted as "the packet was consumed, do not free it." Because no consumer actually took ownership, the RX net_pkt is never returned to the pool and is leaked. The concretely reproducible leak occurs for frames whose EtherType has no registered L3 handler when CONFIG_NET_ETHERNET_FORWARD_UNRECOGNISED_ETHERTYPE is set (default y when CONFIG_NET_SOCKETS_PACKET is enabled): the fall-through L3 dispatch does not overwrite the NET_OK verdict, so ethernet_recv() returns NET_OK and the buffer is never released.

Any device on a bridged L2 segment can emit broadcast/multicast frames carrying an arbitrary EtherType with no authentication. Each such frame permanently consumes one buffer from the finite RX pool (CONFIG_NET_PKT_RX_COUNT), so a brief broadcast flood exhausts the pool and the device can no longer receive traffic until it is rebooted — a persistent denial of service. There is no confidentiality or integrity impact.

The fix makes eth_bridge_handle_locally() propagate the real net_verdict and return NET_CONTINUE for locally-kept frames, writing the bridge interface back through a new dst_iface out-parameter so the packet follows the normal receive path and is unreferenced exactly once.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14696.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-3m4w-wc4v-766q
- https://nvd.nist.gov/vuln/detail/CVE-2026-14696
- https://github.com/zephyrproject-rtos/zephyr/commit/4eb007af465a1d28f2f35d93ecf139cc62c542a7
- https://github.com/zephyrproject-rtos/zephyr
