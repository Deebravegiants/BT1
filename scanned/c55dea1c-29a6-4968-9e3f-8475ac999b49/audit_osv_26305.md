# [H] swiotlb: fix out-of-bounds TLB allocations with CONFIG_SWIOTLB_DYNAMIC

## Summary
Severity: High
Advisory: CVE-2023-52790
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52790
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

swiotlb: fix out-of-bounds TLB allocations with CONFIG_SWIOTLB_DYNAMIC

Limit the free list length to the size of the IO TLB. Transient pool can be
smaller than IO_TLB_SEGSIZE, but the free list is initialized with the
assumption that the total number of slots is a multiple of IO_TLB_SEGSIZE.
As a result, swiotlb_area_find_slots() may allocate slots past the end of
a transient IO TLB buffer.

## References
- https://git.kernel.org/stable/c/53c87e846e335e3c18044c397cc35178163d7827
- https://git.kernel.org/stable/c/ce7612496a4ba6068bc68aa1fa9d947dadb4ad9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52790.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
