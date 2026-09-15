# [H] s390: Disable ARCH_WANT_OPTIMIZE_HUGETLB_VMEMMAP

## Summary
Severity: High
Advisory: CVE-2025-68179
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68179
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390: Disable ARCH_WANT_OPTIMIZE_HUGETLB_VMEMMAP

As reported by Luiz Capitulino enabling HVO on s390 leads to reproducible
crashes. The problem is that kernel page tables are modified without
flushing corresponding TLB entries.

Even if it looks like the empty flush_tlb_all() implementation on s390 is
the problem, it is actually a different problem: on s390 it is not allowed
to replace an active/valid page table entry with another valid page table
entry without the detour over an invalid entry. A direct replacement may
lead to random crashes and/or data corruption.

In order to invalidate an entry special instructions have to be used
(e.g. ipte or idte). Alternatively there are also special instructions
available which allow to replace a valid entry with a different valid
entry (e.g. crdte or cspg).

Given that the HVO code currently does not provide the hooks to allow for
an implementation which is compliant with the s390 architecture
requirements, disable ARCH_WANT_OPTIMIZE_HUGETLB_VMEMMAP again, which is
basically a revert of the original patch which enabled it.

## References
- https://git.kernel.org/stable/c/5e23918e4352288323d13fb511116cdea0234b71
- https://git.kernel.org/stable/c/64e2f60f355e556337fcffe80b9bcff1b22c9c42
- https://git.kernel.org/stable/c/7088465f10816d9425b95740b37c95f082041d76
- https://git.kernel.org/stable/c/d4a8238e5729505b7394ccb007e5dc3e557aa66b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68179.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68179
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
