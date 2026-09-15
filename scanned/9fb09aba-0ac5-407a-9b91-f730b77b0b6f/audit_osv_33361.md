# [H] page_pool: Fix PP_MAGIC_MASK to avoid crashing on some 32-bit arches

## Summary
Severity: High
Advisory: CVE-2025-40199
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40199
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

page_pool: Fix PP_MAGIC_MASK to avoid crashing on some 32-bit arches

Helge reported that the introduction of PP_MAGIC_MASK let to crashes on
boot on his 32-bit parisc machine. The cause of this is the mask is set
too wide, so the page_pool_page_is_pp() incurs false positives which
crashes the machine.

Just disabling the check in page_pool_is_pp() will lead to the page_pool
code itself malfunctioning; so instead of doing this, this patch changes
the define for PP_DMA_INDEX_BITS to avoid mistaking arbitrary kernel
pointers for page_pool-tagged pages.

The fix relies on the kernel pointers that alias with the pp_magic field
always being above PAGE_OFFSET. With this assumption, we can use the
lowest bit of the value of PAGE_OFFSET as the upper bound of the
PP_DMA_INDEX_MASK, which should avoid the false positives.

Because we cannot rely on PAGE_OFFSET always being a compile-time
constant, nor on it always being >0, we fall back to disabling the
dma_index storage when there are not enough bits available. This leaves
us in the situation we were in before the patch in the Fixes tag, but
only on a subset of architecture configurations. This seems to be the
best we can do until the transition to page types in complete for
page_pool pages.

v2:
- Make sure there's at least 8 bits available and that the PAGE_OFFSET
  bit calculation doesn't wrap

## References
- https://git.kernel.org/stable/c/15b8a5b4cdc16e9a8bb2a548e12a0fd92997605a
- https://git.kernel.org/stable/c/95920c2ed02bde551ab654e9749c2ca7bc3100e0
- https://git.kernel.org/stable/c/f62934cea32c8f7b11b747975d69bf5afe4264cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40199.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
