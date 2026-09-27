# [M] CVE-2021-47036

## Summary
Severity: Medium
Advisory: CVE-2021-47036
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47036
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

udp: skip L4 aggregation for UDP tunnel packets

If NETIF_F_GRO_FRAGLIST or NETIF_F_GRO_UDP_FWD are enabled, and there
are UDP tunnels available in the system, udp_gro_receive() could end-up
doing L4 aggregation (either SKB_GSO_UDP_L4 or SKB_GSO_FRAGLIST) at
the outer UDP tunnel level for packets effectively carrying and UDP
tunnel header.

That could cause inner protocol corruption. If e.g. the relevant
packets carry a vxlan header, different vxlan ids will be ignored/
aggregated to the same GSO packet. Inner headers will be ignored, too,
so that e.g. TCP over vxlan push packets will be held in the GRO
engine till the next flush, etc.

Just skip the SKB_GSO_UDP_L4 and SKB_GSO_FRAGLIST code path if the
current packet could land in a UDP tunnel, and let udp_gro_receive()
do GRO via udp_sk(sk)->gro_receive.

The check implemented in this patch is broader than what is strictly
needed, as the existing UDP tunnel could be e.g. configured on top of
a different device: we could end-up skipping GRO at-all for some packets.

Anyhow, that is a very thin corner case and covering it will add quite
a bit of complexity.

v1 -> v2:
 - hopefully clarify the commit message

## References
- https://git.kernel.org/stable/c/18f25dc399901426dff61e676ba603ff52c666f7
- https://git.kernel.org/stable/c/450687386cd16d081b58cd7a342acff370a96078
