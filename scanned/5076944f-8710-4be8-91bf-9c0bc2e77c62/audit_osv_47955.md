# [M] CVE-2017-15589

## Summary
Severity: Medium
Advisory: CVE-2017-15589
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15589
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing x86 HVM guest OS users to obtain sensitive information from the host OS (or an arbitrary guest OS) because intercepted I/O operations can cause a write of data from uninitialized hypervisor stack memory.

## References
- https://support.citrix.com/article/CTX228867
- https://lists.debian.org/debian-lts-announce/2017/11/msg00027.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://www.debian.org/security/2017/dsa-4050
- http://www.securityfocus.com/bid/101496
- http://www.securitytracker.com/id/1039568
- https://security.gentoo.org/glsa/201801-14
- https://xenbits.xen.org/xsa/advisory-239.html
