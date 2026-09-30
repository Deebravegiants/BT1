# [H] mm, slub: do not call do_slab_free for kfence object

## Summary
Severity: High
Advisory: CVE-2024-44973
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44973
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm, slub: do not call do_slab_free for kfence object

In 782f8906f805 the freeing of kfence objects was moved from deep
inside do_slab_free to the wrapper functions outside. This is a nice
change, but unfortunately it missed one spot in __kmem_cache_free_bulk.

This results in a crash like this:

BUG skbuff_head_cache (Tainted: G S  B       E     ): Padding overwritten. 0xffff88907fea0f00-0xffff88907fea0fff @offset=3840

slab_err (mm/slub.c:1129)
free_to_partial_list (mm/slub.c:? mm/slub.c:4036)
slab_pad_check (mm/slub.c:864 mm/slub.c:1290)
check_slab (mm/slub.c:?)
free_to_partial_list (mm/slub.c:3171 mm/slub.c:4036)
kmem_cache_alloc_bulk (mm/slub.c:? mm/slub.c:4495 mm/slub.c:4586 mm/slub.c:4635)
napi_build_skb (net/core/skbuff.c:348 net/core/skbuff.c:527 net/core/skbuff.c:549)

All the other callers to do_slab_free appear to be ok.

Add a kfence_free check in __kmem_cache_free_bulk to avoid the crash.

## References
- https://git.kernel.org/stable/c/a371d558e6f3aed977a8a7346350557de5d25190
- https://git.kernel.org/stable/c/b35cd7f1e969aaa63e6716d82480f6b8a3230949
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44973.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
