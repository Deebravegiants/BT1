# [M] CVE-2019-19579

## Summary
Severity: Medium
Advisory: CVE-2019-19579
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-19579
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing attackers to gain host OS privileges via DMA in a situation where an untrusted domain has access to a physical device (and assignable-add is not used), because of an incomplete fix for CVE-2019-18424. XSA-302 relies on the use of libxl's "assignable-add" feature to prepare devices to be assigned to untrusted guests. Unfortunately, this is not considered a strictly required step for device assignment. The PCI passthrough documentation on the wiki describes alternate ways of preparing devices for assignment, and libvirt uses its own ways as well. Hosts where these "alternate" methods are used will still leave the system in a vulnerable state after the device comes back from a guest. An untrusted domain with access to a physical device can DMA into host memory, leading to privilege escalation. Only systems where guests are given direct access to physical devices capable of DMA (PCI pass-through) are vulnerable. Systems which do not use PCI pass-through are not vulnerable.

## References
- https://seclists.org/bugtraq/2020/Jan/21
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJYT5FNGM7JSVHHW6B22TSAATBOAPFPD/
- https://www.debian.org/security/2020/dsa-4602
- https://www.openwall.com/lists/oss-security/2019/11/26/2
- https://xenbits.xen.org/xsa/advisory-306.html
- http://www.openwall.com/lists/oss-security/2019/12/05/7
- http://xenbits.xen.org/xsa/advisory-306.html
