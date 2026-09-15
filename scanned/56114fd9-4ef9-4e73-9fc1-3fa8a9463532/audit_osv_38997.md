# [H] mm/page_alloc: clear page->private in free_pages_prepare()

## Summary
Severity: High
Advisory: CVE-2026-43303
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43303
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/page_alloc: clear page->private in free_pages_prepare()

Several subsystems (slub, shmem, ttm, etc.) use page->private but don't
clear it before freeing pages.  When these pages are later allocated as
high-order pages and split via split_page(), tail pages retain stale
page->private values.

This causes a use-after-free in the swap subsystem.  The swap code uses
page->private to track swap count continuations, assuming freshly
allocated pages have page->private == 0.  When stale values are present,
swap_count_continued() incorrectly assumes the continuation list is valid
and iterates over uninitialized page->lru containing LIST_POISON values,
causing a crash:

  KASAN: maybe wild-memory-access in range [0xdead000000000100-0xdead000000000107]
  RIP: 0010:__do_sys_swapoff+0x1151/0x1860

Fix this by clearing page->private in free_pages_prepare(), ensuring all
freed pages have clean state regardless of previous use.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/23b82b7a26182ad840ae67d390d7ec9771e8c00f
- https://git.kernel.org/stable/c/3edb8ebbf79b9016040e8f3421d723ae3d542b32
- https://git.kernel.org/stable/c/ac1ea219590c09572ed5992dc233bbf7bb70fef9
- https://git.kernel.org/stable/c/d757c793853ec5483eb41ec2942c300b8fa720fb
- https://git.kernel.org/stable/c/e7790ab165713b79b1617ce659742ceb3a859d05
- https://git.kernel.org/stable/c/f9719e32a67b4b00b3c9b133e8b5ffa72a26b67b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43303.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
