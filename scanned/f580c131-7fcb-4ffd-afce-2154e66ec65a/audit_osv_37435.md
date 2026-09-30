# [H] ocfs2: fix use-after-free in ocfs2_fault() when VM_FAULT_RETRY

## Summary
Severity: High
Advisory: CVE-2026-31597
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31597
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix use-after-free in ocfs2_fault() when VM_FAULT_RETRY

filemap_fault() may drop the mmap_lock before returning VM_FAULT_RETRY,
as documented in mm/filemap.c:

  "If our return value has VM_FAULT_RETRY set, it's because the mmap_lock
  may be dropped before doing I/O or by lock_folio_maybe_drop_mmap()."

When this happens, a concurrent munmap() can call remove_vma() and free
the vm_area_struct via RCU. The saved 'vma' pointer in ocfs2_fault() then
becomes a dangling pointer, and the subsequent trace_ocfs2_fault() call
dereferences it -- a use-after-free.

Fix this by saving ip_blkno as a plain integer before calling
filemap_fault(), and removing vma from the trace event. Since
ip_blkno is copied by value before the lock can be dropped, it
remains valid regardless of what happens to the vma or inode
afterward.

## References
- https://git.kernel.org/stable/c/35c2c05261d6f6d84aaa1355afa201d507943e76
- https://git.kernel.org/stable/c/36539c4d536f851a3b346a6ebb27b51bc3d77a94
- https://git.kernel.org/stable/c/3f5e74b5db9353b01ed50f4de84e75b755f8fbc2
- https://git.kernel.org/stable/c/4cf2768a0291a0cdd0dae801ea0eafa3878a349d
- https://git.kernel.org/stable/c/6f072daefcab1d84ce37c073645615f63be91006
- https://git.kernel.org/stable/c/76a602fdbb78dd05b2da06f74a988cebc97e82d0
- https://git.kernel.org/stable/c/7de554cabf160e331e4442e2a9ad874ca9875921
- https://git.kernel.org/stable/c/925bf22c1b823e231b1baea761fe8a1512e442f2
- https://git.kernel.org/stable/c/d45ff441b416d4aa1af72b1db23d959601c04da2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31597.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
