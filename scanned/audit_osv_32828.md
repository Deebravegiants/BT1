# [H] mm/hugetlb: unshare page tables during VMA split, not before

## Summary
Severity: High
Advisory: CVE-2025-38084
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-28
Source: https://osv.dev/vulnerability/CVE-2025-38084
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: unshare page tables during VMA split, not before

Currently, __split_vma() triggers hugetlb page table unsharing through
vm_ops->may_split().  This happens before the VMA lock and rmap locks are
taken - which is too early, it allows racing VMA-locked page faults in our
process and racing rmap walks from other processes to cause page tables to
be shared again before we actually perform the split.

Fix it by explicitly calling into the hugetlb unshare logic from
__split_vma() in the same place where THP splitting also happens.  At that
point, both the VMA and the rmap(s) are write-locked.

An annoying detail is that we can now call into the helper
hugetlb_unshare_pmds() from two different locking contexts:

1. from hugetlb_split(), holding:
    - mmap lock (exclusively)
    - VMA lock
    - file rmap lock (exclusively)
2. hugetlb_unshare_all_pmds(), which I think is designed to be able to
   call us with only the mmap lock held (in shared mode), but currently
   only runs while holding mmap lock (exclusively) and VMA lock

Backporting note:
This commit fixes a racy protection that was introduced in commit
b30c14cd6102 ("hugetlb: unshare some PMDs when splitting VMAs"); that
commit claimed to fix an issue introduced in 5.13, but it should actually
also go all the way back.

[jannh@google.com: v2]

## References
- https://git.kernel.org/stable/c/081056dc00a27bccb55ccc3c6f230a3d5fd3f7e0
- https://git.kernel.org/stable/c/2511ac64bc1617ca716d3ba8464e481a647c1902
- https://git.kernel.org/stable/c/366298f2b04d2bf1f2f2b7078405bdf9df9bd5d0
- https://git.kernel.org/stable/c/8a21d5584826f4880f45bbf8f72375f4e6c0ff2a
- https://git.kernel.org/stable/c/9cf5b2a3b72c23fb7b84736d5d19ee6ea718762b
- https://git.kernel.org/stable/c/af6cfcd0efb7f051af221c418ec8b37a10211947
- https://git.kernel.org/stable/c/e8847d18cd9fff1edbb45e963d9141273c3b539c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://project-zero.issues.chromium.org/issues/420715744
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38084.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
