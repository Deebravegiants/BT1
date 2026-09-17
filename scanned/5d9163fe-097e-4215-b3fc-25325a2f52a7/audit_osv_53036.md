# [H] CVE-2022-26360

## Summary
Severity: High
Advisory: CVE-2022-26360
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-26360
Type: osv

## Details
IOMMU: RMRR (VT-d) and unity map (AMD-Vi) handling issues T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Certain PCI devices in a system might be assigned Reserved Memory Regions (specified via Reserved Memory Region Reporting, "RMRR") for Intel VT-d or Unity Mapping ranges for AMD-Vi. These are typically used for platform tasks such as legacy USB emulation. Since the precise purpose of these regions is unknown, once a device associated with such a region is active, the mappings of these regions need to remain continuouly accessible by the device. This requirement has been violated. Subsequent DMA or interrupts from the device may have unpredictable behaviour, ranging from IOMMU faults to memory corruption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6ETPM2OVZZ6KOS2L7QO7SIW6XWT5OW3F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHFSRVLM2JUCPDC2KGB7ETPQYJLCGBLD/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5117
- https://xenbits.xenproject.org/xsa/advisory-400.txt
- http://www.openwall.com/lists/oss-security/2022/04/05/3
- http://xenbits.xen.org/xsa/advisory-400.html
