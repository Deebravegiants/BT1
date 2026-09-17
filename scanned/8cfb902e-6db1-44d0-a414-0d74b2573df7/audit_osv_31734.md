# [M] mm: clear uffd-wp PTE/PMD state on mremap()

## Summary
Severity: Medium
Advisory: CVE-2025-21696
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-21696
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: clear uffd-wp PTE/PMD state on mremap()

When mremap()ing a memory region previously registered with userfaultfd as
write-protected but without UFFD_FEATURE_EVENT_REMAP, an inconsistency in
flag clearing leads to a mismatch between the vma flags (which have
uffd-wp cleared) and the pte/pmd flags (which do not have uffd-wp
cleared).  This mismatch causes a subsequent mprotect(PROT_WRITE) to
trigger a warning in page_table_check_pte_flags() due to setting the pte
to writable while uffd-wp is still set.

Fix this by always explicitly clearing the uffd-wp pte/pmd flags on any
such mremap() so that the values are consistent with the existing clearing
of VM_UFFD_WP.  Be careful to clear the logical flag regardless of its
physical form; a PTE bit, a swap PTE bit, or a PTE marker.  Cover PTE,
huge PMD and hugetlb paths.

## References
- https://git.kernel.org/stable/c/0cef0bb836e3cfe00f08f9606c72abd72fe78ca3
- https://git.kernel.org/stable/c/310ac886d68de661c3a334198d8604b722d7fdf8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21696.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
