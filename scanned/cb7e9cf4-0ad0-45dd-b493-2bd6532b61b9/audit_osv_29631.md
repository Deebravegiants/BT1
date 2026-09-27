# [H] mm/vmalloc: fix page mapping if vm_area_alloc_pages() with high order fallback to order 0

## Summary
Severity: High
Advisory: CVE-2024-45022
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45022
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.107, >=6.2.0 <6.6.48, >=6.3.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vmalloc: fix page mapping if vm_area_alloc_pages() with high order fallback to order 0

The __vmap_pages_range_noflush() assumes its argument pages** contains
pages with the same page shift.  However, since commit e9c3cda4d86e ("mm,
vmalloc: fix high order __GFP_NOFAIL allocations"), if gfp_flags includes
__GFP_NOFAIL with high order in vm_area_alloc_pages() and page allocation
failed for high order, the pages** may contain two different page shifts
(high order and order-0).  This could lead __vmap_pages_range_noflush() to
perform incorrect mappings, potentially resulting in memory corruption.

Users might encounter this as follows (vmap_allow_huge = true, 2M is for
PMD_SIZE):

kvmalloc(2M, __GFP_NOFAIL|GFP_X)
    __vmalloc_node_range_noprof(vm_flags=VM_ALLOW_HUGE_VMAP)
        vm_area_alloc_pages(order=9) ---> order-9 allocation failed and fallback to order-0
            vmap_pages_range()
                vmap_pages_range_noflush()
                    __vmap_pages_range_noflush(page_shift = 21) ----> wrong mapping happens

We can remove the fallback code because if a high-order allocation fails,
__vmalloc_node_range_noprof() will retry with order-0.  Therefore, it is
unnecessary to fallback to order-0 here.  Therefore, fix this by removing
the fallback code.

## References
- https://git.kernel.org/stable/c/61ebe5a747da649057c37be1c37eb934b4af79ca
- https://git.kernel.org/stable/c/c91618816f4d21fc574d7577a37722adcd4075b2
- https://git.kernel.org/stable/c/de7bad86345c43cd040ed43e20d9fad78a3ee59f
- https://git.kernel.org/stable/c/fd1ffbb50ef4da5e1378a46616b6d7407dc795da
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45022.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
