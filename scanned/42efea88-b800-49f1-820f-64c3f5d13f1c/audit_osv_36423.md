# [H] net: ti: icssg-prueth: Fix memory leak in XDP_DROP for non-zero-copy mode

## Summary
Severity: High
Advisory: CVE-2026-23453
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23453
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ti: icssg-prueth: Fix memory leak in XDP_DROP for non-zero-copy mode

Page recycling was removed from the XDP_DROP path in emac_run_xdp() to
avoid conflicts with AF_XDP zero-copy mode, which uses xsk_buff_free()
instead.

However, this causes a memory leak when running XDP programs that drop
packets in non-zero-copy mode (standard page pool mode). The pages are
never returned to the page pool, leading to OOM conditions.

Fix this by handling cleanup in the caller, emac_rx_packet().
When emac_run_xdp() returns ICSSG_XDP_CONSUMED for XDP_DROP, the
caller now recycles the page back to the page pool. The zero-copy
path, emac_rx_packet_zc() already handles cleanup correctly with
xsk_buff_free().

## References
- https://git.kernel.org/stable/c/719d3e71691db7c4f1658ba5a6d1472928121594
- https://git.kernel.org/stable/c/d16d57dedcb69c1a1257e0638f8698ce1f0ccbe5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23453.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
