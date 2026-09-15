# [H] mm/khugepaged: fix ->anon_vma race

## Summary
Severity: High
Advisory: CVE-2023-52935
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52935
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/khugepaged: fix ->anon_vma race

If an ->anon_vma is attached to the VMA, collapse_and_free_pmd() requires
it to be locked.

Page table traversal is allowed under any one of the mmap lock, the
anon_vma lock (if the VMA is associated with an anon_vma), and the
mapping lock (if the VMA is associated with a mapping); and so to be
able to remove page tables, we must hold all three of them. 
retract_page_tables() bails out if an ->anon_vma is attached, but does
this check before holding the mmap lock (as the comment above the check
explains).

If we racily merged an existing ->anon_vma (shared with a child
process) from a neighboring VMA, subsequent rmap traversals on pages
belonging to the child will be able to see the page tables that we are
concurrently removing while assuming that nothing else can access them.

Repeat the ->anon_vma check once we hold the mmap lock to ensure that
there really is no concurrent page table access.

Hitting this bug causes a lockdep warning in collapse_and_free_pmd(),
in the line "lockdep_assert_held_write(&vma->anon_vma->root->rwsem)". 
It can also lead to use-after-free access.

## References
- https://git.kernel.org/stable/c/023f47a8250c6bdb4aebe744db4bf7f73414028b
- https://git.kernel.org/stable/c/352fbf61ce776fef18dca6a68680a6cd943dac95
- https://git.kernel.org/stable/c/abdf3c33918185c3e8ffeb09ed3e334b3d7df47c
- https://git.kernel.org/stable/c/acb08187b5a83cdb9ac4112fae9e18cf983b0128
- https://git.kernel.org/stable/c/cee956ab1efbd858b4ca61c8b474af5aa24b29a6
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52935.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
