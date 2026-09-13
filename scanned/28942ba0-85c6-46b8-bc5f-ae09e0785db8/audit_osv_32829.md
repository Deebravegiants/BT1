# [H] mm/hugetlb: fix huge_pmd_unshare() vs GUP-fast race

## Summary
Severity: High
Advisory: CVE-2025-38085
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-28
Source: https://osv.dev/vulnerability/CVE-2025-38085
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: fix huge_pmd_unshare() vs GUP-fast race

huge_pmd_unshare() drops a reference on a page table that may have
previously been shared across processes, potentially turning it into a
normal page table used in another process in which unrelated VMAs can
afterwards be installed.

If this happens in the middle of a concurrent gup_fast(), gup_fast() could
end up walking the page tables of another process.  While I don't see any
way in which that immediately leads to kernel memory corruption, it is
really weird and unexpected.

Fix it with an explicit broadcast IPI through tlb_remove_table_sync_one(),
just like we do in khugepaged when removing page tables for a THP
collapse.

## References
- https://git.kernel.org/stable/c/034a52b5ef57c9c8225d94e9067f3390bb33922f
- https://git.kernel.org/stable/c/1013af4f585fccc4d3e5c5824d174de2257f7d6d
- https://git.kernel.org/stable/c/952596b08c74e8fe9e2883d1dc8a8f54a37384ec
- https://git.kernel.org/stable/c/a3d864c901a300c295692d129159fc3001a56185
- https://git.kernel.org/stable/c/a6bfeb97941a9187833b526bc6cc4ff5706d0ce9
- https://git.kernel.org/stable/c/b7754d3aa7bf9f62218d096c0c8f6c13698fac8b
- https://git.kernel.org/stable/c/fe684290418ef9ef76630072086ee530b92f02b8
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://project-zero.issues.chromium.org/issues/420715744
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38085.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
