# [H] net: airoha: Fix DMA direction for NPU mailbox buffer

## Summary
Severity: High
Advisory: CVE-2026-68330
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68330
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: airoha: Fix DMA direction for NPU mailbox buffer

airoha_npu_send_msg() always maps the mailbox buffer with DMA_TO_DEVICE,
but some callers expect the NPU to write response data back into the
same buffer:

- airoha_npu_wlan_msg_get() (NPU_OP_GET): NPU writes response into
  the buffer, then the caller reads it via memcpy()
- airoha_npu_ppe_stats_setup() (NPU_OP_SET): NPU writes back
  npu_stats_addr field in the response

On non-cache-coherent architectures like EN7581 (Cortex-A53 without
hardware cache coherency for NPU DMA), DMA_TO_DEVICE unmap is a no-op
— it does not invalidate the CPU cache. If the NPU-written cache line
is still present in the CPU cache when the caller reads the buffer,
the CPU observes stale data instead of the NPU response.

This is a timing-sensitive bug: small mailbox buffers (~24 bytes)
typically fit in a single cache line and may survive in the cache
until the caller reads them, producing silent data corruption rather
than a crash. The bug is more likely to trigger when the caller reads
the response immediately after dma_unmap_single() without intervening
cache-evicting operations.

Fix by using DMA_BIDIRECTIONAL for both map and unmap, which ensures
dma_unmap_single() invalidates the CPU cache on non-coherent systems.
The mailbox buffers are small so there is no performance concern.

## References
- https://git.kernel.org/stable/c/4c4d866a64f36718cbcdf20add372a599dd44311
- https://git.kernel.org/stable/c/6f884eb87a79e0c482baef2ad96c96b81d024235
- https://git.kernel.org/stable/c/76fc5604308a109bf5838c2a0a0eb3ac6819f1ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68330.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
