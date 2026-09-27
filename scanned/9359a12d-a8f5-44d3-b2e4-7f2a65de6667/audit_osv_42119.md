# [H] net: qualcomm: rmnet: validate MAP frame length before ingress parsing

## Summary
Severity: High
Advisory: CVE-2026-64550
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64550
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qualcomm: rmnet: validate MAP frame length before ingress parsing

When ingress deaggregation is disabled, rmnet_map_ingress_handler() passes
the skb straight to __rmnet_map_ingress_handler(), skipping the length
validation that rmnet_map_deaggregate() performs on the aggregated path.
The parser then dereferences the MAP header and csum header/trailer based on
the on-wire pkt_len without checking skb->len, so a short frame is read out
of bounds:

  BUG: KASAN: slab-out-of-bounds in rmnet_map_checksum_downlink_packet
  Read of size 1 at addr ffff88801118ed00 by task exploit/147
  Call Trace:
   ...
   rmnet_map_checksum_downlink_packet (drivers/net/ethernet/qualcomm/rmnet/rmnet_map_data.c:413)
   __rmnet_map_ingress_handler (drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c:96)
   rmnet_rx_handler (drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c:129)
   __netif_receive_skb_core.constprop.0 (net/core/dev.c:6089)
   netif_receive_skb (net/core/dev.c:6460)
   tun_get_user (drivers/net/tun.c:1955)
   tun_chr_write_iter (drivers/net/tun.c:2001)
   vfs_write (fs/read_write.c:688)
   ksys_write (fs/read_write.c:740)
   do_syscall_64 (arch/x86/entry/syscall_64.c:94)
   ...

Factor that validation out of rmnet_map_deaggregate() into
rmnet_map_validate_packet_len() and run it on the no-aggregation path too.
The MAP header is bounds-checked first, since this path can receive a frame
shorter than the header.

## References
- https://git.kernel.org/stable/c/00f4c366dbca16a40772c3b7ec2d8cba839e9724
- https://git.kernel.org/stable/c/14eb0c9491385d5361a292ea4974aec0e6887299
- https://git.kernel.org/stable/c/1b12612c367e4be9b0814c0468e7e687835315b4
- https://git.kernel.org/stable/c/231a8a4b76cb1b1827b3b19d7b3603642f5aaaef
- https://git.kernel.org/stable/c/3868c3244369ab709a90c9aad7534d406009b824
- https://git.kernel.org/stable/c/a54d76d176e50d2fdbd39b7231efe256170339e4
- https://git.kernel.org/stable/c/ed25befc8c36f896b5878f9078faddb67fd7e2d0
- https://git.kernel.org/stable/c/f0f1887a9e30712a1df03e152dce6fb91344b1f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64550.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
