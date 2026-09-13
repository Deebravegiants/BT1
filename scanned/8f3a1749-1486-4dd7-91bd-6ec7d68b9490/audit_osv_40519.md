# [H] fbdev: omap2: fix use-after-free in omapfb_mmap

## Summary
Severity: High
Advisory: CVE-2026-53401
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53401
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: omap2: fix use-after-free in omapfb_mmap

omapfb_mmap() has a race condition with OMAPFB_SETUP_PLANE ioctl that
can lead to use-after-free:

The fb_mmap() entry point holds mm_lock but not lock (fb_info->lock),
while ioctl handlers like OMAPFB_SETUP_PLANE hold lock but not mm_lock.
This allows concurrent execution.

In omapfb_mmap():
1. rg = omapfb_get_mem_region(ofbi->region);      // Get old region ref
2. start = omapfb_get_region_paddr(ofbi);          // Read from NEW region
3. len = fix->smem_len;                             // Read from NEW region
4. vm_iomap_memory(vma, start, len);               // Map NEW region memory
5. atomic_inc(&rg->map_count);                      // Increment OLD region!

Concurrently, OMAPFB_SETUP_PLANE can:
- Reassign ofbi->region = new_rg
- Update fix->smem_len
- OMAPFB_SETUP_MEM then checks NEW region's map_count (0!) and frees it

This leaves userspace with a mapping to freed physical memory.

The fix is to read all required values (start, len) from the same
region reference (rg) that will have its map_count incremented,
preventing the region from being freed while still mapped.

## References
- https://git.kernel.org/stable/c/6eb6ebcc8590007ad59ddccc8b5f9201655b33f8
- https://git.kernel.org/stable/c/7958e67375aa111522086286bba13cfc0816ce8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
