# [M] CVE-2018-10472

## Summary
Severity: Medium
Advisory: CVE-2018-10472
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-04-27
Source: https://osv.dev/vulnerability/CVE-2018-10472
Type: osv

## Details
An issue was discovered in Xen through 4.10.x allowing x86 HVM guest OS users (in certain configurations) to read arbitrary dom0 files via QMP live insertion of a CDROM, in conjunction with specifying the target file as the backing file of a snapshot.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00021.html
- http://www.securityfocus.com/bid/104002
- https://security.gentoo.org/glsa/201810-06
- https://www.debian.org/security/2018/dsa-4201
- https://xenbits.xen.org/xsa/advisory-258.html
