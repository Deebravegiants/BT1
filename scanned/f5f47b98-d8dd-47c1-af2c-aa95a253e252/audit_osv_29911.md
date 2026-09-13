# [H] mm/hugetlb.c: fix UAF of vma in hugetlb fault pathway

## Summary
Severity: High
Advisory: CVE-2024-47676
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47676
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb.c: fix UAF of vma in hugetlb fault pathway

Syzbot reports a UAF in hugetlb_fault().  This happens because
vmf_anon_prepare() could drop the per-VMA lock and allow the current VMA
to be freed before hugetlb_vma_unlock_read() is called.

We can fix this by using a modified version of vmf_anon_prepare() that
doesn't release the VMA lock on failure, and then release it ourselves
after hugetlb_vma_unlock_read().

## References
- https://git.kernel.org/stable/c/98b74bb4d7e96b4da5ef3126511febe55b76b807
- https://git.kernel.org/stable/c/d59ebc99dee0a2687a26df94b901eb8216dbf876
- https://git.kernel.org/stable/c/e897d184a8dd4a4e1f39c8c495598e4d9472776c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47676.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
