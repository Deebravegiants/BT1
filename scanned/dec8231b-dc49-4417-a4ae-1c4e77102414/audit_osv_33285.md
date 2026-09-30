# [H] mm/hugetlb: fix folio is still mapped when deleted

## Summary
Severity: High
Advisory: CVE-2025-40006
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/CVE-2025-40006
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: fix folio is still mapped when deleted

Migration may be raced with fallocating hole.  remove_inode_single_folio
will unmap the folio if the folio is still mapped.  However, it's called
without folio lock.  If the folio is migrated and the mapped pte has been
converted to migration entry, folio_mapped() returns false, and won't
unmap it.  Due to extra refcount held by remove_inode_single_folio,
migration fails, restores migration entry to normal pte, and the folio is
mapped again.  As a result, we triggered BUG in filemap_unaccount_folio.

The log is as follows:
 BUG: Bad page cache in process hugetlb  pfn:156c00
 page: refcount:515 mapcount:0 mapping:0000000099fef6e1 index:0x0 pfn:0x156c00
 head: order:9 mapcount:1 entire_mapcount:1 nr_pages_mapped:0 pincount:0
 aops:hugetlbfs_aops ino:dcc dentry name(?):"my_hugepage_file"
 flags: 0x17ffffc00000c1(locked|waiters|head|node=0|zone=2|lastcpupid=0x1fffff)
 page_type: f4(hugetlb)
 page dumped because: still mapped when deleted
 CPU: 1 UID: 0 PID: 395 Comm: hugetlb Not tainted 6.17.0-rc5-00044-g7aac71907bde-dirty #484 NONE
 Hardware name: QEMU Ubuntu 24.04 PC (i440FX + PIIX, 1996), BIOS 0.0.0 02/06/2015
 Call Trace:
  <TASK>
  dump_stack_lvl+0x4f/0x70
  filemap_unaccount_folio+0xc4/0x1c0
  __filemap_remove_folio+0x38/0x1c0
  filemap_remove_folio+0x41/0xd0
  remove_inode_hugepages+0x142/0x250
  hugetlbfs_fallocate+0x471/0x5a0
  vfs_fallocate+0x149/0x380

Hold folio lock before checking if the folio is mapped to avold race with
migration.

## References
- https://git.kernel.org/stable/c/21ee79ce938127f88fe07e409c1817f477dbe7ea
- https://git.kernel.org/stable/c/3e851448078f5b01f6264915df3cfef75e323a12
- https://git.kernel.org/stable/c/7b7387650dcf2881fd8bb55bcf3c8bd6c9542dd7
- https://git.kernel.org/stable/c/910d7749346c4b0acdc6e4adfdc4a9984281a206
- https://git.kernel.org/stable/c/91f548e920fbf8be3f285bfa3fa045ae017e836d
- https://git.kernel.org/stable/c/bc1c9ce8aeff45318332035dbef9713fb9e982d7
- https://git.kernel.org/stable/c/c1dc0524ab2cc3982d4e0d2bfac71a0cd4d65c39
- https://git.kernel.org/stable/c/c9c2a51f91aea70e89b496cac360cd795a2b3c26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40006.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
