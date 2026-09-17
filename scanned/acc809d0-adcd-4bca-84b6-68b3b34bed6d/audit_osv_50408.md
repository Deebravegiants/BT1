# [H] CVE-2020-15565

## Summary
Severity: High
Advisory: CVE-2020-15565
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15565
Type: osv

## Details
An issue was discovered in Xen through 4.13.x, allowing x86 Intel HVM guest OS users to cause a host OS denial of service or possibly gain privileges because of insufficient cache write-back under VT-d. When page tables are shared between IOMMU and CPU, changes to them require flushing of both TLBs. Furthermore, IOMMUs may be non-coherent, and hence prior to flushing IOMMU TLBs, a CPU cache also needs writing back to memory after changes were made. Such writing back of cached data was missing in particular when splitting large page mappings into smaller granularity ones. A malicious guest may be able to retain read/write DMA access to frames returned to Xen's free pool, and later reused for another purpose. Host crashes (leading to a Denial of Service) and privilege escalation cannot be ruled out. Xen versions from at least 3.2 onwards are affected. Only x86 Intel systems are affected. x86 AMD as well as Arm systems are not affected. Only x86 HVM guests using hardware assisted paging (HAP), having a passed through PCI device assigned, and having page table sharing enabled can leverage the vulnerability. Note that page table sharing will be enabled (by default) only if Xen considers IOMMU and CPU large page size support compatible.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXESCOVI7AVRNC7HEAMFM7PMEO6D3AUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB3QJJZV23Z2IDYEMIHELWYSQBUEW6JP/
- https://security.gentoo.org/glsa/202007-02
- https://www.debian.org/security/2020/dsa-4723
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00031.html
- http://www.openwall.com/lists/oss-security/2020/07/07/4
- http://xenbits.xen.org/xsa/advisory-321.html
