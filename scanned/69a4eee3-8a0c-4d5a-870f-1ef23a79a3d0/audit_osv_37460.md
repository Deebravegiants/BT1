# [H] mm: filemap: fix nr_pages calculation overflow in filemap_map_pages()

## Summary
Severity: High
Advisory: CVE-2026-31648
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31648
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.135, >=6.7.0 <6.12.82, >=6.12.0 <6.18.23, >=6.13.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: filemap: fix nr_pages calculation overflow in filemap_map_pages()

When running stress-ng on my Arm64 machine with v7.0-rc3 kernel, I
encountered some very strange crash issues showing up as "Bad page state":

"
[  734.496287] BUG: Bad page state in process stress-ng-env  pfn:415735fb
[  734.496427] page: refcount:0 mapcount:1 mapping:0000000000000000 index:0x4cf316 pfn:0x415735fb
[  734.496434] flags: 0x57fffe000000800(owner_2|node=1|zone=2|lastcpupid=0x3ffff)
[  734.496439] raw: 057fffe000000800 0000000000000000 dead000000000122 0000000000000000
[  734.496440] raw: 00000000004cf316 0000000000000000 0000000000000000 0000000000000000
[  734.496442] page dumped because: nonzero mapcount
"

After analyzing this page’s state, it is hard to understand why the
mapcount is not 0 while the refcount is 0, since this page is not where
the issue first occurred.  By enabling the CONFIG_DEBUG_VM config, I can
reproduce the crash as well and captured the first warning where the issue
appears:

"
[  734.469226] page: refcount:33 mapcount:0 mapping:00000000bef2d187 index:0x81a0 pfn:0x415735c0
[  734.469304] head: order:5 mapcount:0 entire_mapcount:0 nr_pages_mapped:0 pincount:0
[  734.469315] memcg:ffff000807a8ec00
[  734.469320] aops:ext4_da_aops ino:100b6f dentry name(?):"stress-ng-mmaptorture-9397-0-2736200540"
[  734.469335] flags: 0x57fffe400000069(locked|uptodate|lru|head|node=1|zone=2|lastcpupid=0x3ffff)
......
[  734.469364] page dumped because: VM_WARN_ON_FOLIO((_Generic((page + nr_pages - 1),
const struct page *: (const struct folio *)_compound_head(page + nr_pages - 1), struct page *:
(struct folio *)_compound_head(page + nr_pages - 1))) != folio)
[  734.469390] ------------[ cut here ]------------
[  734.469393] WARNING: ./include/linux/rmap.h:351 at folio_add_file_rmap_ptes+0x3b8/0x468,
CPU#90: stress-ng-mlock/9430
[  734.469551]  folio_add_file_rmap_ptes+0x3b8/0x468 (P)
[  734.469555]  set_pte_range+0xd8/0x2f8
[  734.469566]  filemap_map_folio_range+0x190/0x400
[  734.469579]  filemap_map_pages+0x348/0x638
[  734.469583]  do_fault_around+0x140/0x198
......
[  734.469640]  el0t_64_sync+0x184/0x188
"

The code that triggers the warning is: "VM_WARN_ON_FOLIO(page_folio(page +
nr_pages - 1) != folio, folio)", which indicates that set_pte_range()
tried to map beyond the large folio’s size.

By adding more debug information, I found that 'nr_pages' had overflowed
in filemap_map_pages(), causing set_pte_range() to establish mappings for
a range exceeding the folio size, potentially corrupting fields of pages
that do not belong to this folio (e.g., page->_mapcount).

After above analysis, I think the possible race is as follows:

CPU 0                                                  CPU 1
filemap_map_pages()                                   ext4_setattr()
   //get and lock folio with old inode->i_size
   next_uptodate_folio()

                                                          .......
                                                          //shrink the inode->i_size
                                                          i_size_write(inode, attr->ia_size);

   //calculate the end_pgoff with the new inode->i_size
   file_end = DIV_ROUND_UP(i_size_read(mapping->host), PAGE_SIZE) - 1;
   end_pgoff = min(end_pgoff, file_end);

   ......
   //nr_pages can be overflowed, cause xas.xa_index > end_pgoff
   end = folio_next_index(folio) - 1;
   nr_pages = min(end, end_pgoff) - xas.xa_index + 1;

   ......
   //map large folio
   filemap_map_folio_range()
                                                          ......
                                                          //truncate folios
                                                          truncate_pagecache(inode, inode->i_size);

To fix this issue, move the 'end_pgoff' calculation before
next_uptodate_folio(), so the retrieved folio stays consistent with the
file end to avoid 
---truncated---

## References
- https://git.kernel.org/stable/c/576543bedd616254032d4ebe54a90076f9e31740
- https://git.kernel.org/stable/c/633ab680c405ac390e6bec5b74aaf46197c837b6
- https://git.kernel.org/stable/c/88591194df736a508dd5461ab2167a61e98caac1
- https://git.kernel.org/stable/c/9316a820b9aae07d44469d6485376dad824c5b3f
- https://git.kernel.org/stable/c/f58df566524ebcdfa394329c64f47e3c9257516e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31648.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31648
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
