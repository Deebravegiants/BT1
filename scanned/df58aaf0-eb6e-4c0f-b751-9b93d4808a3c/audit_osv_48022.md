# [M] CVE-2017-17046

## Summary
Severity: Medium
Advisory: CVE-2017-17046
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/CVE-2017-17046
Type: osv

## Details
An issue was discovered in Xen through 4.9.x on the ARM platform allowing guest OS users to obtain sensitive information from DRAM after a reboot, because disjoint blocks, and physical addresses that do not start at zero, are mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://security.gentoo.org/glsa/201801-14
- https://xenbits.xen.org/xsa/advisory-245.html
