# [H] iommu/iova: Fix alloc iova overflows issue

## Summary
Severity: High
Advisory: CVE-2023-52910
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2023-52910
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.89, >=5.16.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/iova: Fix alloc iova overflows issue

In __alloc_and_insert_iova_range, there is an issue that retry_pfn
overflows. The value of iovad->anchor.pfn_hi is ~0UL, then when
iovad->cached_node is iovad->anchor, curr_iova->pfn_hi + 1 will
overflow. As a result, if the retry logic is executed, low_pfn is
updated to 0, and then new_pfn < low_pfn returns false to make the
allocation successful.

This issue occurs in the following two situations:
1. The first iova size exceeds the domain size. When initializing
iova domain, iovad->cached_node is assigned as iovad->anchor. For
example, the iova domain size is 10M, start_pfn is 0x1_F000_0000,
and the iova size allocated for the first time is 11M. The
following is the log information, new->pfn_lo is smaller than
iovad->cached_node.

Example log as follows:
[  223.798112][T1705487] sh: [name:iova&]__alloc_and_insert_iova_range
start_pfn:0x1f0000,retry_pfn:0x0,size:0xb00,limit_pfn:0x1f0a00
[  223.799590][T1705487] sh: [name:iova&]__alloc_and_insert_iova_range
success start_pfn:0x1f0000,new->pfn_lo:0x1efe00,new->pfn_hi:0x1f08ff

2. The node with the largest iova->pfn_lo value in the iova domain
is deleted, iovad->cached_node will be updated to iovad->anchor,
and then the alloc iova size exceeds the maximum iova size that can
be allocated in the domain.

After judging that retry_pfn is less than limit_pfn, call retry_pfn+1
to fix the overflow issue.

## References
- https://git.kernel.org/stable/c/61cbf790e7329ed78877560be7136f0b911bba7f
- https://git.kernel.org/stable/c/c929a230c84441e400c32e7b7b4ab763711fb63e
- https://git.kernel.org/stable/c/dcdb3ba7e2a8caae7bfefd603bc22fd0ce9a389c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52910.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
