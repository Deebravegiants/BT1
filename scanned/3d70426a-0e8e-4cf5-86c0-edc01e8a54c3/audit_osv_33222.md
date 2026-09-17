# [M] mm/vmalloc, mm/kasan: respect gfp mask in kasan_populate_vmalloc()

## Summary
Severity: Medium
Advisory: CVE-2025-39910
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39910
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vmalloc, mm/kasan: respect gfp mask in kasan_populate_vmalloc()

kasan_populate_vmalloc() and its helpers ignore the caller's gfp_mask and
always allocate memory using the hardcoded GFP_KERNEL flag.  This makes
them inconsistent with vmalloc(), which was recently extended to support
GFP_NOFS and GFP_NOIO allocations.

Page table allocations performed during shadow population also ignore the
external gfp_mask.  To preserve the intended semantics of GFP_NOFS and
GFP_NOIO, wrap the apply_to_page_range() calls into the appropriate
memalloc scope.

xfs calls vmalloc with GFP_NOFS, so this bug could lead to deadlock.

There was a report here
https://lkml.kernel.org/r/686ea951.050a0220.385921.0016.GAE@google.com

This patch:
 - Extends kasan_populate_vmalloc() and helpers to take gfp_mask;
 - Passes gfp_mask down to alloc_pages_bulk() and __get_free_page();
 - Enforces GFP_NOFS/NOIO semantics with memalloc_*_save()/restore()
   around apply_to_page_range();
 - Updates vmalloc.c and percpu allocator call sites accordingly.

## References
- https://git.kernel.org/stable/c/33b95d90427cb4babf32059e323a6d0c027610fe
- https://git.kernel.org/stable/c/79357cd06d41d0f5a11b17d7c86176e395d10ef2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39910.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
