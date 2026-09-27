# [H] CVE-2019-13164

## Summary
Severity: High
Advisory: CVE-2019-13164
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-13164
Type: osv

## Details
qemu-bridge-helper.c in QEMU 3.1 and 4.0.0 does not ensure that a network interface name (obtained from bridge.conf or a --br=bridge option) is limited to the IFNAMSIZ size, which can lead to an ACL bypass.

## References
- http://www.securityfocus.com/bid/109054
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00008.html
- http://www.openwall.com/lists/oss-security/2019/07/02/2
- https://lists.debian.org/debian-lts-announce/2019/09/msg00021.html
- https://seclists.org/bugtraq/2019/Aug/41
- https://seclists.org/bugtraq/2019/Sep/3
- https://security.gentoo.org/glsa/202003-66
- https://usn.ubuntu.com/4191-1/
- https://usn.ubuntu.com/4191-2/
- https://www.debian.org/security/2019/dsa-4506
- https://www.debian.org/security/2019/dsa-4512
- https://github.com/qemu/qemu/commit/03d7712b4bcd47bfe0fe14ba2fffa87e111fa086
- https://lists.gnu.org/archive/html/qemu-devel/2019-07/msg00145.html
