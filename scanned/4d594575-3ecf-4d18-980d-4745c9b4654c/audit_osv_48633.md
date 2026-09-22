# [M] CVE-2018-10471

## Summary
Severity: Medium
Advisory: CVE-2018-10471
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-04-27
Source: https://osv.dev/vulnerability/CVE-2018-10471
Type: osv

## Details
An issue was discovered in Xen through 4.10.x allowing x86 PV guest OS users to cause a denial of service (out-of-bounds zero write and hypervisor crash) via unexpected INT 80 processing, because of an incorrect fix for CVE-2017-5754.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://security.gentoo.org/glsa/201810-06
- https://www.debian.org/security/2018/dsa-4201
- https://xenbits.xen.org/xsa/advisory-259.html
- http://www.securityfocus.com/bid/104003
