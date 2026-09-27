# [H] iommu/sva: invalidate stale IOTLB entries for kernel address space

## Summary
Severity: High
Advisory: CVE-2025-71202
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2025-71202
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/sva: invalidate stale IOTLB entries for kernel address space

Introduce a new IOMMU interface to flush IOTLB paging cache entries for
the CPU kernel address space.  This interface is invoked from the x86
architecture code that manages combined user and kernel page tables,
specifically before any kernel page table page is freed and reused.

This addresses the main issue with vfree() which is a common occurrence
and can be triggered by unprivileged users.  While this resolves the
primary problem, it doesn't address some extremely rare case related to
memory unplug of memory that was present as reserved memory at boot, which
cannot be triggered by unprivileged users.  The discussion can be found at
the link below.

Enable SVA on x86 architecture since the IOMMU can now receive
notification to flush the paging cache before freeing the CPU kernel page
table pages.

## References
- https://git.kernel.org/stable/c/9f0a7ab700f8620e433b05c57fbd26c92ea186d9
- https://git.kernel.org/stable/c/e37d5a2d60a338c5917c45296bac65da1382eda5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71202.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
