# [H] mm/hugetlb: do not call vma_add_reservation upon ENOMEM

## Summary
Severity: High
Advisory: CVE-2024-39477
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39477
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: do not call vma_add_reservation upon ENOMEM

sysbot reported a splat [1] on __unmap_hugepage_range().  This is because
vma_needs_reservation() can return -ENOMEM if
allocate_file_region_entries() fails to allocate the file_region struct
for the reservation.

Check for that and do not call vma_add_reservation() if that is the case,
otherwise region_abort() and region_del() will see that we do not have any
file_regions.

If we detect that vma_needs_reservation() returned -ENOMEM, we clear the
hugetlb_restore_reserve flag as if this reservation was still consumed, so
free_huge_folio() will not increment the resv count.

[1] https://lore.kernel.org/linux-mm/0000000000004096100617c58d54@google.com/T/#ma5983bc1ab18a54910da83416b3f89f3c7ee43aa

## References
- https://git.kernel.org/stable/c/8daf9c702ee7f825f0de8600abff764acfedea13
- https://git.kernel.org/stable/c/aa998f9dcb34c28448f86e8f5490f20d5eb0eac7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39477.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
