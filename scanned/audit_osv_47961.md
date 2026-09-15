# [H] CVE-2017-15595

## Summary
Severity: High
Advisory: CVE-2017-15595
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15595
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing x86 PV guest OS users to cause a denial of service (unbounded recursion, stack consumption, and hypervisor crash) or possibly gain privileges via crafted page-table stacking.

## References
- https://support.citrix.com/article/CTX228867
- https://www.exploit-db.com/exploits/43014/
- https://lists.debian.org/debian-lts-announce/2017/11/msg00027.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00021.html
- https://www.debian.org/security/2017/dsa-4050
- https://security.gentoo.org/glsa/201801-14
- https://xenbits.xen.org/xsa/advisory-240.html
