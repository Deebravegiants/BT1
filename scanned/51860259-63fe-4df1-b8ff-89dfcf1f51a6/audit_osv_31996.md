# [H] x86/mm/pat: Fix VM_PAT handling when fork() fails in copy_page_range()

## Summary
Severity: High
Advisory: CVE-2025-22090
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22090
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <6.1.160, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/mm/pat: Fix VM_PAT handling when fork() fails in copy_page_range()

If track_pfn_copy() fails, we already added the dst VMA to the maple
tree. As fork() fails, we'll cleanup the maple tree, and stumble over
the dst VMA for which we neither performed any reservation nor copied
any page tables.

Consequently untrack_pfn() will see VM_PAT and try obtaining the
PAT information from the page table -- which fails because the page
table was not copied.

The easiest fix would be to simply clear the VM_PAT flag of the dst VMA
if track_pfn_copy() fails. However, the whole thing is about "simply"
clearing the VM_PAT flag is shaky as well: if we passed track_pfn_copy()
and performed a reservation, but copying the page tables fails, we'll
simply clear the VM_PAT flag, not properly undoing the reservation ...
which is also wrong.

So let's fix it properly: set the VM_PAT flag only if the reservation
succeeded (leaving it clear initially), and undo the reservation if
anything goes wrong while copying the page tables: clearing the VM_PAT
flag after undoing the reservation.

Note that any copied page table entries will get zapped when the VMA will
get removed later, after copy_page_range() succeeded; as VM_PAT is not set
then, we won't try cleaning VM_PAT up once more and untrack_pfn() will be
happy. Note that leaving these page tables in place without a reservation
is not a problem, as we are aborting fork(); this process will never run.

A reproducer can trigger this usually at the first try:

  https://gitlab.com/davidhildenbrand/scratchspace/-/raw/main/reproducers/pat_fork.c

  WARNING: CPU: 26 PID: 11650 at arch/x86/mm/pat/memtype.c:983 get_pat_info+0xf6/0x110
  Modules linked in: ...
  CPU: 26 UID: 0 PID: 11650 Comm: repro3 Not tainted 6.12.0-rc5+ #92
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-2.fc40 04/01/2014
  RIP: 0010:get_pat_info+0xf6/0x110
  ...
  Call Trace:
   <TASK>
   ...
   untrack_pfn+0x52/0x110
   unmap_single_vma+0xa6/0xe0
   unmap_vmas+0x105/0x1f0
   exit_mmap+0xf6/0x460
   __mmput+0x4b/0x120
   copy_process+0x1bf6/0x2aa0
   kernel_clone+0xab/0x440
   __do_sys_clone+0x66/0x90
   do_syscall_64+0x95/0x180

Likely this case was missed in:

  d155df53f310 ("x86/mm/pat: clear VM_PAT if copy_p4d_range failed")

... and instead of undoing the reservation we simply cleared the VM_PAT flag.

Keep the documentation of these functions in include/linux/pgtable.h,
one place is more than sufficient -- we should clean that up for the other
functions like track_pfn_remap/untrack_pfn separately.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/8d6373f83f367dbed316ddeb178130a3a64b5b67
- https://git.kernel.org/stable/c/a6623712ba8449876f0b3de9462831523fb851e4
- https://git.kernel.org/stable/c/b07398e8a5da517083f5c3f2daa8f6681b48ab28
- https://git.kernel.org/stable/c/da381c33f3aa6406406c9fdf07b8b0b63e0ce722
- https://git.kernel.org/stable/c/dc84bc2aba85a1508f04a936f9f9a15f64ebfb31
- https://git.kernel.org/stable/c/de6185b8892d88142ef69768fe4077cbf40109c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22090.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
