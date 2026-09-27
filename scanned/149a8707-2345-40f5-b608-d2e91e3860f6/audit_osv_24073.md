# [H] mm/hugetlb: avoid corrupting page->mapping in hugetlb_mcopy_atomic_pte

## Summary
Severity: High
Advisory: CVE-2022-49991
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49991
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.65, >=5.16.0 <5.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: avoid corrupting page->mapping in hugetlb_mcopy_atomic_pte

In MCOPY_ATOMIC_CONTINUE case with a non-shared VMA, pages in the page
cache are installed in the ptes.  But hugepage_add_new_anon_rmap is called
for them mistakenly because they're not vm_shared.  This will corrupt the
page->mapping used by page cache code.

## References
- https://git.kernel.org/stable/c/3ada1b3e58db255a14ec73a59d7913e84dc5a8a4
- https://git.kernel.org/stable/c/ab74ef708dc51df7cf2b8a890b9c6990fac5c0c6
- https://git.kernel.org/stable/c/da60ddd80d09f8371fbba1a238a4b318d13ba698
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49991.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
