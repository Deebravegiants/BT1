# [H] CVE-2021-28702

## Summary
Severity: High
Advisory: CVE-2021-28702
CVSS: 7.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-10-06
Source: https://osv.dev/vulnerability/CVE-2021-28702
Type: osv

## Details
PCI devices with RMRRs not deassigned correctly Certain PCI devices in a system might be assigned Reserved Memory Regions (specified via Reserved Memory Region Reporting, "RMRR"). These are typically used for platform tasks such as legacy USB emulation. If such a device is passed through to a guest, then on guest shutdown the device is not properly deassigned. The IOMMU configuration for these devices which are not properly deassigned ends up pointing to a freed data structure, including the IO Pagetables. Subsequent DMA or interrupts from the device will have unpredictable behaviour, ranging from IOMMU faults to memory corruption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2OIHEJ3R3EH5DYI2I5UMD2ULJ2ELA3EX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FDPRMOBBLS74ONYP3IXZZXSTLKR7GRQB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRAWV6PO2KUGVZTESERECOBUBZ6X45I7/
- https://www.debian.org/security/2021/dsa-5017
- https://xenbits.xenproject.org/xsa/advisory-386.txt
- http://www.openwall.com/lists/oss-security/2021/10/07/2
- https://security.gentoo.org/glsa/202208-23
