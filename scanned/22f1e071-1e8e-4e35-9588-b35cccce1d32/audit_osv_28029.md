# [H] fork: defer linking file vma until vma is fully initialized

## Summary
Severity: High
Advisory: CVE-2024-27022
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27022
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.134, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fork: defer linking file vma until vma is fully initialized

Thorvald reported a WARNING [1]. And the root cause is below race:

 CPU 1					CPU 2
 fork					hugetlbfs_fallocate
  dup_mmap				 hugetlbfs_punch_hole
   i_mmap_lock_write(mapping);
   vma_interval_tree_insert_after -- Child vma is visible through i_mmap tree.
   i_mmap_unlock_write(mapping);
   hugetlb_dup_vma_private -- Clear vma_lock outside i_mmap_rwsem!
					 i_mmap_lock_write(mapping);
   					 hugetlb_vmdelete_list
					  vma_interval_tree_foreach
					   hugetlb_vma_trylock_write -- Vma_lock is cleared.
   tmp->vm_ops->open -- Alloc new vma_lock outside i_mmap_rwsem!
					   hugetlb_vma_unlock_write -- Vma_lock is assigned!!!
					 i_mmap_unlock_write(mapping);

hugetlb_dup_vma_private() and hugetlb_vm_op_open() are called outside
i_mmap_rwsem lock while vma lock can be used in the same time.  Fix this
by deferring linking file vma until vma is fully initialized.  Those vmas
should be initialized first before they can be used.

## References
- https://git.kernel.org/stable/c/04b0c41912349aff11a1bbaef6a722bd7fbb90ac
- https://git.kernel.org/stable/c/0c42f7e039aba3de6d7dbf92da708e2b2ecba557
- https://git.kernel.org/stable/c/2e5cbab8ccbfc7d4a3d8a21d3c2a1f2c1aa29b5b
- https://git.kernel.org/stable/c/35e351780fa9d8240dd6f7e4f245f9ea37e96c19
- https://git.kernel.org/stable/c/abdb88dd272bbeb93efe01d8e0b7b17e24af3a34
- https://git.kernel.org/stable/c/cec11fa2eb512ebe3a459c185f4aca1d44059bbf
- https://git.kernel.org/stable/c/dd782da470761077f4d1120e191f1a35787cda6e
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27022.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
