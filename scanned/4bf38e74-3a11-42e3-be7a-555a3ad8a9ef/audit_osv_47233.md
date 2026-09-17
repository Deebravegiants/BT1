# [M] CVE-2016-1571

## Summary
Severity: Medium
Advisory: CVE-2016-1571
CVSS: 6.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-01-22
Source: https://osv.dev/vulnerability/CVE-2016-1571
Type: osv

## Details
The paging_invlpg function in include/asm-x86/paging.h in Xen 3.3.x through 4.6.x, when using shadow mode paging or nested virtualization is enabled, allows local HVM guest users to cause a denial of service (host crash) via a non-canonical guest address in an INVVPID instruction, which triggers a hypervisor bug check.

## References
- http://support.citrix.com/article/CTX205496
- http://www.debian.org/security/2016/dsa-3519
- http://www.securitytracker.com/id/1034745
- http://xenbits.xen.org/xsa/advisory-168.html
