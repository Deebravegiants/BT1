# [H] CVE-2021-45417

## Summary
Severity: High
Advisory: CVE-2021-45417
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-20
Source: https://osv.dev/vulnerability/CVE-2021-45417
Type: osv

## Details
AIDE before 0.17.4 allows local users to obtain root privileges via crafted file metadata (such as XFS extended attributes or tmpfs ACLs), because of a heap-based buffer overflow.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00024.html
- https://security.gentoo.org/glsa/202311-07
- https://www.debian.org/security/2022/dsa-5051
- http://www.openwall.com/lists/oss-security/2022/01/20/3
- https://www.ipi.fi/pipermail/aide/2022-January/001713.html
- https://www.openwall.com/lists/oss-security/2022/01/20/3
