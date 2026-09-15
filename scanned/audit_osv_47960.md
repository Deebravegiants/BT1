# [H] CVE-2017-15594

## Summary
Severity: High
Advisory: CVE-2017-15594
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15594
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing x86 SVM PV guest OS users to cause a denial of service (hypervisor crash) or gain privileges because IDT settings are mishandled during CPU hotplugging.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00021.html
- https://support.citrix.com/article/CTX228867
- http://www.securitytracker.com/id/1039568
- https://security.gentoo.org/glsa/201801-14
- https://www.debian.org/security/2017/dsa-4050
- https://xenbits.xen.org/xsa/advisory-244.html
