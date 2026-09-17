# [M] SiWx91x WiFi driver double-unref / use-after-free of caller-owned TX net_pkt

## Summary
Severity: Medium
Advisory: CVE-2026-14366
Aliases: GHSA-f9qq-jv4w-pqxg
CVSS: 6.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-14366
Type: osv

## Details
The Silicon Labs SiWx917 WiFi driver's transmit callback siwx91x_send() in drivers/wifi/siwx91x/siwx91x_wifi.c frees a network packet it does not own. In the Zephyr TX path the net_pkt is owned by the L2/networking stack; the driver only borrows it to copy the frame bytes into a local net_buf. Before the fix, after transmitting, siwx91x_send() additionally called net_pkt_unref(pkt) on the caller-owned packet, dropping its last reference and returning it to the shared packet pool prematurely. This code path is compiled in by default (CONFIG_WIFI_SILABS_SIWX91X_NET_STACK_NATIVE).

The caller, ethernet_send() in subsys/net/l2/ethernet/ethernet.c, keeps using the packet after the driver returns: it reads net_pkt_get_len(pkt), updates TX statistics, and then performs its own net_pkt_unref(pkt). Because the driver already released the packet, these are use-after-free reads followed by a second unref (a double free). When concurrent network activity recycles the freed slab slot between the two unrefs, the trailing unref decrements a different, live packet's reference count and frees it, corrupting the net_pkt pool shared by both the receive and transmit paths.

The defect is exercised by ordinary transmission over the native-stack SiWx917 WiFi interface, and an adjacent attacker on the same WiFi network can induce transmissions (for example ARP or ICMP echo replies, or TCP handshakes) to drive the path. The primary observable impact is loss of availability (transmit hangs and crashes from pool corruption), with race-dependent memory corruption of the kernel networking buffer pool. The fix removes the erroneous net_pkt_unref(pkt) from siwx91x_send(); the driver's receive-path unref, which correctly frees a packet the driver itself allocated, is unaffected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14366.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-f9qq-jv4w-pqxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-14366
- https://github.com/zephyrproject-rtos/zephyr/commit/680a351c7dd0ba46eb67d9c0e7165d901a7bd3d1
- https://github.com/zephyrproject-rtos/zephyr
