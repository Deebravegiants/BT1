# [H] mm: hugetlb: independent PMD page table shared count

## Summary
Severity: High
Advisory: CVE-2024-57883
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57883
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.72, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: hugetlb: independent PMD page table shared count

The folio refcount may be increased unexpectly through try_get_folio() by
caller such as split_huge_pages.  In huge_pmd_unshare(), we use refcount
to check whether a pmd page table is shared.  The check is incorrect if
the refcount is increased by the above caller, and this can cause the page
table leaked:

 BUG: Bad page state in process sh  pfn:109324
 page: refcount:0 mapcount:0 mapping:0000000000000000 index:0x66 pfn:0x109324
 flags: 0x17ffff800000000(node=0|zone=2|lastcpupid=0xfffff)
 page_type: f2(table)
 raw: 017ffff800000000 0000000000000000 0000000000000000 0000000000000000
 raw: 0000000000000066 0000000000000000 00000000f2000000 0000000000000000
 page dumped because: nonzero mapcount
 ...
 CPU: 31 UID: 0 PID: 7515 Comm: sh Kdump: loaded Tainted: G    B              6.13.0-rc2master+ #7
 Tainted: [B]=BAD_PAGE
 Hardware name: QEMU KVM Virtual Machine, BIOS 0.0.0 02/06/2015
 Call trace:
  show_stack+0x20/0x38 (C)
  dump_stack_lvl+0x80/0xf8
  dump_stack+0x18/0x28
  bad_page+0x8c/0x130
  free_page_is_bad_report+0xa4/0xb0
  free_unref_page+0x3cc/0x620
  __folio_put+0xf4/0x158
  split_huge_pages_all+0x1e0/0x3e8
  split_huge_pages_write+0x25c/0x2d8
  full_proxy_write+0x64/0xd8
  vfs_write+0xcc/0x280
  ksys_write+0x70/0x110
  __arm64_sys_write+0x24/0x38
  invoke_syscall+0x50/0x120
  el0_svc_common.constprop.0+0xc8/0xf0
  do_el0_svc+0x24/0x38
  el0_svc+0x34/0x128
  el0t_64_sync_handler+0xc8/0xd0
  el0t_64_sync+0x190/0x198

The issue may be triggered by damon, offline_page, page_idle, etc, which
will increase the refcount of page table.

1. The page table itself will be discarded after reporting the
   "nonzero mapcount".

2. The HugeTLB page mapped by the page table miss freeing since we
   treat the page table as shared and a shared page table will not be
   unmapped.

Fix it by introducing independent PMD page table shared count.  As
described by comment, pt_index/pt_mm/pt_frag_refcount are used for s390
gmap, x86 pgds and powerpc, pt_share_count is used for x86/arm64/riscv
pmds, so we can reuse the field as pt_share_count.

## References
- https://git.kernel.org/stable/c/02333ac1c35370517a19a4a131332a9690c6a5c7
- https://git.kernel.org/stable/c/2e31443a0d18ae43b9d29e02bf0563f07772193d
- https://git.kernel.org/stable/c/56b274473d6e7e7375f2d0a2b4aca11d67c6b52f
- https://git.kernel.org/stable/c/59d9094df3d79443937add8700b2ef1a866b1081
- https://git.kernel.org/stable/c/8410996eb6fea116fe1483ed977aacf580eee7b4
- https://git.kernel.org/stable/c/94b4b41d0cdf5cfd4d4325bc0e6e9e0d0e996133
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57883.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
