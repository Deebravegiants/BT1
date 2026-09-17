# [H] mm: hugetlb: fix UAF in hugetlb_handle_userfault

## Summary
Severity: High
Advisory: CVE-2022-50630
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2022-50630
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: hugetlb: fix UAF in hugetlb_handle_userfault

The vma_lock and hugetlb_fault_mutex are dropped before handling userfault
and reacquire them again after handle_userfault(), but reacquire the
vma_lock could lead to UAF[1,2] due to the following race,

hugetlb_fault
  hugetlb_no_page
    /*unlock vma_lock */
    hugetlb_handle_userfault
      handle_userfault
        /* unlock mm->mmap_lock*/
                                           vm_mmap_pgoff
                                             do_mmap
                                               mmap_region
                                                 munmap_vma_range
                                                   /* clean old vma */
        /* lock vma_lock again  <--- UAF */
    /* unlock vma_lock */

Since the vma_lock will unlock immediately after
hugetlb_handle_userfault(), let's drop the unneeded lock and unlock in
hugetlb_handle_userfault() to fix the issue.

[1] https://lore.kernel.org/linux-mm/000000000000d5e00a05e834962e@google.com/
[2] https://lore.kernel.org/linux-mm/20220921014457.1668-1-liuzixian4@huawei.com/

## References
- https://git.kernel.org/stable/c/0db2efb3bff879566f05341d94c3de00ac95c4cc
- https://git.kernel.org/stable/c/45c33966759ea1b4040c08dacda99ef623c0ca29
- https://git.kernel.org/stable/c/78504bcedb2f1bbfb353b4d233c24d641c4dda33
- https://git.kernel.org/stable/c/958f32ce832ba781ac20e11bb2d12a9352ea28fc
- https://git.kernel.org/stable/c/dd691973f67b2800a97db723b1ff6f07fdcf7f5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50630.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50630
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
