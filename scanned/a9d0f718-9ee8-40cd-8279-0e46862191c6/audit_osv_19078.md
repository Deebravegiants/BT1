# [M] CVE-2020-7039

## Summary
Severity: Medium
Advisory: CVE-2020-7039
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2020-7039
Type: osv

## Details
tcp_emu in tcp_subr.c in libslirp 4.1.0, as used in QEMU 4.2.0, mismanages memory, as demonstrated by IRC DCC commands in EMU_IRC. This can cause a heap-based buffer overflow or other out-of-bounds access which can lead to a DoS or potential execute arbitrary code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00007.html
- https://access.redhat.com/errata/RHSA-2020:0348
- https://access.redhat.com/errata/RHSA-2020:0775
- https://lists.debian.org/debian-lts-announce/2020/01/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00012.html
- https://seclists.org/bugtraq/2020/Feb/0
- https://security.gentoo.org/glsa/202005-02
- https://usn.ubuntu.com/4283-1/
- https://www.debian.org/security/2020/dsa-4616
- http://www.openwall.com/lists/oss-security/2020/01/16/2
- https://gitlab.freedesktop.org/slirp/libslirp/commit/2655fffed7a9e765bcb4701dd876e9dab975f289
- https://gitlab.freedesktop.org/slirp/libslirp/commit/82ebe9c370a0e2970fb5695aa19aa5214a6a1c80
- https://gitlab.freedesktop.org/slirp/libslirp/commit/ce131029d6d4a405cb7d3ac6716d03e58fb4a5d9
