# [H] CVE-2021-28706

## Summary
Severity: High
Advisory: CVE-2021-28706
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/CVE-2021-28706
Type: osv

## Details
guests may exceed their designated memory limit When a guest is permitted to have close to 16TiB of memory, it may be able to issue hypercalls to increase its memory allocation beyond the administrator established limit. This is a result of a calculation done with 32-bit precision, which may overflow. It would then only be the overflowed (and hence small) number which gets compared against the established upper bound.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I7ZGWVVRI4XY2XSTBI3XEMWBXPDVX6OT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PXUI4VMD52CH3T7YXAG3J2JW7ZNN3SXF/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2021/dsa-5017
- https://xenbits.xenproject.org/xsa/advisory-385.txt
