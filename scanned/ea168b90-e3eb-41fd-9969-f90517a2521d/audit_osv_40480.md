# [H] net: enetc: fix NTMP DMA use-after-free issue

## Summary
Severity: High
Advisory: CVE-2026-53300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53300
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: enetc: fix NTMP DMA use-after-free issue

The AI-generated review reported a potential DMA use-after-free issue
[1]. If netc_xmit_ntmp_cmd() times out and returns an error, the pending
command is not explicitly aborted, while ntmp_free_data_mem()
unconditionally frees the DMA buffer. If the buffer has already been
reallocated elsewhere, this may lead to silent memory corruption. Because
the hardware eventually processes the pending command and perform a DMA
write of the response to the physical address of the freed buffer.

To resolve this issue, this patch does the following modifications:

1. Convert cbdr->ring_lock from a spinlock to a mutex

The lock was originally a spinlock in case NTMP operations might be
invoked from atomic context. After downstream support for all NTMP
tables, no such usage has materialized. A mutex lock is now required
because the driver now needs to reclaim used BDs and release associated
DMA memory within the lock's context, while dma_free_coherent() might
sleep.

2. Introduce software command BD (struct netc_swcbd)

The hardware write-back overwrites the addr and len fields of the BD,
so the driver cannot rely on the hardware BD to free the associated DMA
memory. The driver now maintains a software shadow BD storing the DMA
buffer pointer, DMA address, and size. And netc_xmit_ntmp_cmd() only
reclaims older BDs when the number of used BDs reaches
NETC_CBDR_CLEAN_WORK (16). The software BD enables correct DMA memory
release. With this, struct ntmp_dma_buf and ntmp_free_data_mem() are no
longer needed and are removed.

3. Require callers to hold ring_lock across netc_xmit_ntmp_cmd()

netc_xmit_ntmp_cmd() releases the ring_lock before the caller finishes
consuming the response. At this point, if a concurrent thread submits
a new command, it may trigger ntmp_clean_cbdr() and free the DMA buffer
while it is still in use. Move ring_lock ownership to the caller to
ensure the response buffer cannot be reclaimed prematurely. So the
helpers ntmp_select_and_lock_cbdr() and ntmp_unlock_cbdr() are added.

These changes eliminate the DMA use-after-free condition and ensure safe
and consistent BD reclamation and DMA buffer lifecycle management.

## References
- https://git.kernel.org/stable/c/37c8933064be714ee672b0a0523c2fd045b73b3d
- https://git.kernel.org/stable/c/3cade698881eb238f88cbbfec82acc2110440a3f
- https://git.kernel.org/stable/c/655d9ce9b1d3db0aa5271acb5e5101c66bd0d58b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53300.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
