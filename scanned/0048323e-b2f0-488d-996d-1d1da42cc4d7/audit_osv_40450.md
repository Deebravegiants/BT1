# [H] net/mlx5e: xsk: Fix DMA and xdp_frame leak on XDP_TX xmit failure

## Summary
Severity: High
Advisory: CVE-2026-53229
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53229
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: xsk: Fix DMA and xdp_frame leak on XDP_TX xmit failure

In the XSK branch of mlx5e_xmit_xdp_buff(), when sq->xmit_xdp_frame()
returns false (e.g. XDPSQ is full), the function returns without
unmapping the DMA address or freeing the xdp_frame allocated by
xdp_convert_zc_to_xdp_frame(). The xdpi_fifo push only happens on
success, so the completion path cannot recover these entries.

With CONFIG_DMA_API_DEBUG=y, the leak surfaces on driver unbind:

  DMA-API: pci 0000:08:00.0: device driver has pending DMA
  allocations while released from device [count=1116]
  One of leaked entries details: [device address=0x000000010ffd7028]
  [size=1534 bytes] [mapped with DMA_TO_DEVICE] [mapped as phy]
  WARNING: kernel/dma/debug.c:881 at dma_debug_device_change+0x127/0x180
  ...
  DMA-API: Mapped at:
   debug_dma_map_phys+0x4b/0xd0
   dma_map_phys+0xfd/0x2d0
   mlx5e_xdp_handle+0x5ae/0xac0 [mlx5_core]
   mlx5e_xsk_skb_from_cqe_mpwrq_linear+0xc4/0x170 [mlx5_core]
   mlx5e_handle_rx_cqe_mpwrq+0xc1/0x290 [mlx5_core]

Add the missing unmap + xdp_return_frame, matching the cleanup already
done in mlx5e_xdp_xmit(). has_frags is rejected earlier in this branch,
so no per-frag unmap is needed.

## References
- https://git.kernel.org/stable/c/0aabca726b43d833721034e97d99efcc8237b22a
- https://git.kernel.org/stable/c/2789b74ae1f4b68333c9d5eec2f3354d07b16e61
- https://git.kernel.org/stable/c/7b3eeba50fbc3b45f279037c29a87a90e8bac1e1
- https://git.kernel.org/stable/c/b69004f5a6ad32da84d8aa5b23b9c0caafe6252e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53229.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53229
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
