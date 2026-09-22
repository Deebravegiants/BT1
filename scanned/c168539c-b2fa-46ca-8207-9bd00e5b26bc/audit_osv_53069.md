# [M] CVE-2022-2787

## Summary
Severity: Medium
Advisory: CVE-2022-2787
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-08-27
Source: https://osv.dev/vulnerability/CVE-2022-2787
Type: osv

## Details
Schroot before 1.6.13 had too permissive rules on chroot or session names, allowing a denial of service on the schroot service for all users that may start a schroot session.

## References
- https://lists.debian.org/debian-lts-announce/2022/08/msg00007.html
- https://lists.debian.org/debian-security-announce/2022/msg00182.html
- https://security.gentoo.org/glsa/202210-11
- https://codeberg.org/shelter/reschroot/commit/6f7166a285e1e97aea390be633591f9791b29a6d
