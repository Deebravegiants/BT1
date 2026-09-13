# [H] iommu: disable SVA when CONFIG_X86 is set

## Summary
Severity: High
Advisory: CVE-2025-71089
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71089
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu: disable SVA when CONFIG_X86 is set

Patch series "Fix stale IOTLB entries for kernel address space", v7.

This proposes a fix for a security vulnerability related to IOMMU Shared
Virtual Addressing (SVA).  In an SVA context, an IOMMU can cache kernel
page table entries.  When a kernel page table page is freed and
reallocated for another purpose, the IOMMU might still hold stale,
incorrect entries.  This can be exploited to cause a use-after-free or
write-after-free condition, potentially leading to privilege escalation or
data corruption.

This solution introduces a deferred freeing mechanism for kernel page
table pages, which provides a safe window to notify the IOMMU to
invalidate its caches before the page is reused.


This patch (of 8):

In the IOMMU Shared Virtual Addressing (SVA) context, the IOMMU hardware
shares and walks the CPU's page tables.  The x86 architecture maps the
kernel's virtual address space into the upper portion of every process's
page table.  Consequently, in an SVA context, the IOMMU hardware can walk
and cache kernel page table entries.

The Linux kernel currently lacks a notification mechanism for kernel page
table changes, specifically when page table pages are freed and reused. 
The IOMMU driver is only notified of changes to user virtual address
mappings.  This can cause the IOMMU's internal caches to retain stale
entries for kernel VA.

Use-After-Free (UAF) and Write-After-Free (WAF) conditions arise when
kernel page table pages are freed and later reallocated.  The IOMMU could
misinterpret the new data as valid page table entries.  The IOMMU might
then walk into attacker-controlled memory, leading to arbitrary physical
memory DMA access or privilege escalation.  This is also a
Write-After-Free issue, as the IOMMU will potentially continue to write
Accessed and Dirty bits to the freed memory while attempting to walk the
stale page tables.

Currently, SVA contexts are unprivileged and cannot access kernel
mappings.  However, the IOMMU will still walk kernel-only page tables all
the way down to the leaf entries, where it realizes the mapping is for the
kernel and errors out.  This means the IOMMU still caches these
intermediate page table entries, making the described vulnerability a real
concern.

Disable SVA on x86 architecture until the IOMMU can receive notification
to flush the paging cache before freeing the CPU kernel page table pages.

## References
- https://git.kernel.org/stable/c/240cd7f2812cc25496b12063d11c823618f364e9
- https://git.kernel.org/stable/c/72f98ef9a4be30d2a60136dd6faee376f780d06c
- https://git.kernel.org/stable/c/7cad37e358970af1bb49030ff01f06a69fa7d985
- https://git.kernel.org/stable/c/b34289505180a83607fcfdce14b5a290d0528476
- https://git.kernel.org/stable/c/c2c3f1a3fd74ef16cf115f0c558616a13a8471b4
- https://git.kernel.org/stable/c/c341dee80b5df49a936182341b36395c831c2661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71089.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
