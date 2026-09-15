# [M] CVE-2020-8608

## Summary
Severity: Medium
Advisory: CVE-2020-8608
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2020-8608
Type: osv

## Details
In libslirp 4.1.0, as used in QEMU 4.2.0, tcp_subr.c misuses snprintf return values, leading to a buffer overflow in later code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00007.html
- https://gitlab.freedesktop.org/slirp/libslirp/-/tags/v4.1.0
- https://lists.debian.org/debian-lts-announce/2020/03/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00012.html
- https://security.gentoo.org/glsa/202003-66
- https://security.netapp.com/advisory/ntap-20201001-0002/
- https://usn.ubuntu.com/4283-1/
- https://www.debian.org/security/2020/dsa-4733
- https://gitlab.freedesktop.org/slirp/libslirp/commit/68ccb8021a838066f0951d4b2817eb6b6f10a843
- https://www.openwall.com/lists/oss-security/2020/02/06/2
