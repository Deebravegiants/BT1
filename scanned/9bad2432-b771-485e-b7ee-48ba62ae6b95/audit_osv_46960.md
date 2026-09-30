# [M] CVE-2015-8552

## Summary
Severity: Medium
Advisory: CVE-2015-8552
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-8552
Type: osv

## Details
The PCI backend driver in Xen, when running on an x86 system and using Linux 3.1.x through 4.3.x as the driver domain, allows local guest administrators to generate a continuous stream of WARN messages and cause a denial of service (disk consumption) by leveraging a system with access to a passed-through MSI or MSI-X capable physical PCI device and XEN_PCI_OP_enable_msi operations, aka "Linux pciback missing sanity checks."

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.debian.org/security/2016/dsa-3434
- http://www.securityfocus.com/bid/79546
- http://www.securitytracker.com/id/1034480
- http://xenbits.xen.org/xsa/advisory-157.html
- https://security.gentoo.org/glsa/201604-03
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
