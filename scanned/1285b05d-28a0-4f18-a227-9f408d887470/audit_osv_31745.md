# [M] powerpc/pseries/iommu: Don't unset window if it was never set

## Summary
Severity: Medium
Advisory: CVE-2025-21713
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21713
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/pseries/iommu: Don't unset window if it was never set

On pSeries, when user attempts to use the same vfio container used by
different iommu group, the spapr_tce_set_window() returns -EPERM
and the subsequent cleanup leads to the below crash.

   Kernel attempted to read user page (308) - exploit attempt?
   BUG: Kernel NULL pointer dereference on read at 0x00000308
   Faulting instruction address: 0xc0000000001ce358
   Oops: Kernel access of bad area, sig: 11 [#1]
   NIP:  c0000000001ce358 LR: c0000000001ce05c CTR: c00000000005add0
   <snip>
   NIP [c0000000001ce358] spapr_tce_unset_window+0x3b8/0x510
   LR [c0000000001ce05c] spapr_tce_unset_window+0xbc/0x510
   Call Trace:
     spapr_tce_unset_window+0xbc/0x510 (unreliable)
     tce_iommu_attach_group+0x24c/0x340 [vfio_iommu_spapr_tce]
     vfio_container_attach_group+0xec/0x240 [vfio]
     vfio_group_fops_unl_ioctl+0x548/0xb00 [vfio]
     sys_ioctl+0x754/0x1580
     system_call_exception+0x13c/0x330
     system_call_vectored_common+0x15c/0x2ec
   <snip>
   --- interrupt: 3000

Fix this by having null check for the tbl passed to the
spapr_tce_unset_window().

## References
- https://git.kernel.org/stable/c/17391cb2613b82f8c405570fea605af3255ff8d2
- https://git.kernel.org/stable/c/ac12372a13dab3f7a2762db240bd180de8ef1e5e
- https://git.kernel.org/stable/c/b853ff0b514c1df314246fcf94744005914b48cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21713.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
