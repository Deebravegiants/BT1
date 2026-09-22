# [H] CVE-2017-15588

## Summary
Severity: High
Advisory: CVE-2017-15588
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15588
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing x86 PV guest OS users to execute arbitrary code on the host OS because of a race condition that can cause a stale TLB entry.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2017/11/msg00027.html
- https://support.citrix.com/article/CTX228867
- https://security.gentoo.org/glsa/201801-14
- https://www.debian.org/security/2017/dsa-4050
- http://www.securityfocus.com/bid/101490
- http://www.securitytracker.com/id/1039568
- https://xenbits.xen.org/xsa/advisory-241.html
