# [H] x86/mm: Fix flush_tlb_range() when used for zapping normal PMDs

## Summary
Severity: High
Advisory: CVE-2025-22045
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22045
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/mm: Fix flush_tlb_range() when used for zapping normal PMDs

On the following path, flush_tlb_range() can be used for zapping normal
PMD entries (PMD entries that point to page tables) together with the PTE
entries in the pointed-to page table:

    collapse_pte_mapped_thp
      pmdp_collapse_flush
        flush_tlb_range

The arm64 version of flush_tlb_range() has a comment describing that it can
be used for page table removal, and does not use any last-level
invalidation optimizations. Fix the X86 version by making it behave the
same way.

Currently, X86 only uses this information for the following two purposes,
which I think means the issue doesn't have much impact:

 - In native_flush_tlb_multi() for checking if lazy TLB CPUs need to be
   IPI'd to avoid issues with speculative page table walks.
 - In Hyper-V TLB paravirtualization, again for lazy TLB stuff.

The patch "x86/mm: only invalidate final translations with INVLPGB" which
is currently under review (see
<https://lore.kernel.org/all/20241230175550.4046587-13-riel@surriel.com/>)
would probably be making the impact of this a lot worse.

## References
- https://git.kernel.org/stable/c/0708fd6bd8161871bfbadced2ca4319b84ab44fe
- https://git.kernel.org/stable/c/0a8f806ea6b5dd64b3d1f05ff774817d5f7ddbd1
- https://git.kernel.org/stable/c/320ac1af4c0bdb92c864dc9250d1329234820edf
- https://git.kernel.org/stable/c/3ef938c3503563bfc2ac15083557f880d29c2e64
- https://git.kernel.org/stable/c/556d446068f90981e5d71ca686bdaccdd545d491
- https://git.kernel.org/stable/c/618d5612ecb7bfc1c85342daafeb2b47e29e77a3
- https://git.kernel.org/stable/c/7085895c59e4057ffae17f58990ccb630087d0d2
- https://git.kernel.org/stable/c/78d6f9a9eb2a5da6fcbd76d6191d24b0dcc321be
- https://git.kernel.org/stable/c/93224deb50a8d20df3884f3672ce9f982129aa50
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22045.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
