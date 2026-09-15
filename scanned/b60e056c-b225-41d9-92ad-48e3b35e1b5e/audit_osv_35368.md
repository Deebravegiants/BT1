# [H] dmaengine: mmp_pdma: Fix race condition in mmp_pdma_residue()

## Summary
Severity: High
Advisory: CVE-2025-71221
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2025-71221
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: mmp_pdma: Fix race condition in mmp_pdma_residue()

Add proper locking in mmp_pdma_residue() to prevent use-after-free when
accessing descriptor list and descriptor contents.

The race occurs when multiple threads call tx_status() while the tasklet
on another CPU is freeing completed descriptors:

CPU 0                              CPU 1
-----                              -----
mmp_pdma_tx_status()
mmp_pdma_residue()
  -> NO LOCK held
     list_for_each_entry(sw, ..)
                                   DMA interrupt
                                   dma_do_tasklet()
                                     -> spin_lock(&desc_lock)
                                        list_move(sw->node, ...)
                                        spin_unlock(&desc_lock)
  |                                     dma_pool_free(sw) <- FREED!
  -> access sw->desc <- UAF!

This issue can be reproduced when running dmatest on the same channel with
multiple threads (threads_per_chan > 1).

Fix by protecting the chain_running list iteration and descriptor access
with the chan->desc_lock spinlock.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3f0e0e2d9e752570041e95fd04635e2580097819
- https://git.kernel.org/stable/c/9f665b3c3d9a168410251f27a5d019b7bf93185c
- https://git.kernel.org/stable/c/a143545855bc2c6e1330f6f57ae375ac44af00a7
- https://git.kernel.org/stable/c/dfb5e05227745de43b7fd589721817a4337c970d
- https://git.kernel.org/stable/c/eba0c75670c022cb1f948600db972524bcfe8166
- https://git.kernel.org/stable/c/fc023b8fab057f0c910856ff36d3e12a30b7af4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71221.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
