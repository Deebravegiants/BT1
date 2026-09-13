# [M] CVE-2021-3308

## Summary
Severity: Medium
Advisory: CVE-2021-3308
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3308
Type: osv

## Details
An issue was discovered in Xen 4.12.3 through 4.12.4 and 4.13.1 through 4.14.x. An x86 HVM guest with PCI pass through devices can force the allocation of all IDT vectors on the system by rebooting itself with MSI or MSI-X capabilities enabled and entries setup. Such reboots will leak any vectors used by the MSI(-X) entries that the guest might had enabled, and hence will lead to vector exhaustion on the system, not allowing further PCI pass through devices to work properly. HVM guests with PCI pass through devices can mount a Denial of Service (DoS) attack affecting the pass through of PCI devices to other guests or the hardware domain. In the latter case, this would affect the entire host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S5C42TMQYB6SDVT2MPFEWY65A6RSUVBN/
- https://security.gentoo.org/glsa/202107-30
- http://www.openwall.com/lists/oss-security/2021/01/26/4
- http://xenbits.xen.org/xsa/advisory-360.html
