# [H] net: Stop leased rxq before uninstalling its memory provider

## Summary
Severity: High
Advisory: CVE-2026-74285
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74285
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: Stop leased rxq before uninstalling its memory provider

netif_rxq_cleanup_unlease() tears down the memory provider that was
installed on a physical RX queue through a netkit queue lease. It
currently revokes the provider's DMA mappings before stopping the
physical queue:

  __netif_mp_uninstall_rxq(virt_rxq, p);            /* DMA unmap */
  __netif_mp_close_rxq(phys_rxq->dev, rxq_idx, p);  /* queue stop */

This inverts the ordering used by the regular teardown paths (normal
device unregister and the io_uring zcrx close path), which stop the
queue before revoking the provider's mappings.

With the physical queue still live, its NAPI can keep consuming
net_iov entries from the page_pool alloc cache after the
__netif_mp_uninstall_rxq() has already cleared their dma_addr,
opening a window for the device to DMA to a stale or zero address.

Fix it by swapping the two calls so the queue is stopped (and its
NAPI quiesced) before the provider is uninstalled. No functional
regression was observed across repeated runs of the nk_qlease.py
HW selftest, which exercises the lease teardown path; this was
tested against fbnic QEMU emulation.

## References
- https://git.kernel.org/stable/c/03f4c6ed3cffbfce0b85a3a0193d08a46692a9f8
- https://git.kernel.org/stable/c/37314c9dbe95b4d924c7b61aaf563cec4f4e4133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74285.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
