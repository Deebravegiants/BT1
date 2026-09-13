# [C] net: ti: icssg-prueth: fix use-after-free of CPPI descriptor in RX path

## Summary
Severity: Critical
Advisory: CVE-2026-31501
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31501
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ti: icssg-prueth: fix use-after-free of CPPI descriptor in RX path

cppi5_hdesc_get_psdata() returns a pointer into the CPPI descriptor.
In both emac_rx_packet() and emac_rx_packet_zc(), the descriptor is
freed via k3_cppi_desc_pool_free() before the psdata pointer is used
by emac_rx_timestamp(), which dereferences psdata[0] and psdata[1].
This constitutes a use-after-free on every received packet that goes
through the timestamp path.

Defer the descriptor free until after all accesses through the psdata
pointer are complete. For emac_rx_packet(), move the free into the
requeue label so both early-exit and success paths free the descriptor
after all accesses are done. For emac_rx_packet_zc(), move the free to
the end of the loop body after emac_dispatch_skb_zc() (which calls
emac_rx_timestamp()) has returned.

## References
- https://git.kernel.org/stable/c/d5827316debcb677679bb014885d7be92c410e11
- https://git.kernel.org/stable/c/eb8c426c9803beb171f89d15fea17505eb517714
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31501.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31501
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
