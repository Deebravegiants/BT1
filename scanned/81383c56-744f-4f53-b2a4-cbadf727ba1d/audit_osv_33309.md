# [H] iommu/vt-d: Disallow dirty tracking if incoherent page walk

## Summary
Severity: High
Advisory: CVE-2025-40058
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40058
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Disallow dirty tracking if incoherent page walk

Dirty page tracking relies on the IOMMU atomically updating the dirty bit
in the paging-structure entry. For this operation to succeed, the paging-
structure memory must be coherent between the IOMMU and the CPU. In
another word, if the iommu page walk is incoherent, dirty page tracking
doesn't work.

The Intel VT-d specification, Section 3.10 "Snoop Behavior" states:

"Remapping hardware encountering the need to atomically update A/EA/D bits
 in a paging-structure entry that is not snooped will result in a non-
 recoverable fault."

To prevent an IOMMU from being incorrectly configured for dirty page
tracking when it is operating in an incoherent mode, mark SSADS as
supported only when both ecap_slads and ecap_smpwc are supported.

## References
- https://git.kernel.org/stable/c/57f55048e564dedd8a4546d018e29d6bbfff0a7e
- https://git.kernel.org/stable/c/8d096ce0e87bdc361f0b25d7943543bc53aa0b9e
- https://git.kernel.org/stable/c/ebe16d245a00626bb87163862a1b07daf5475a3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40058.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
