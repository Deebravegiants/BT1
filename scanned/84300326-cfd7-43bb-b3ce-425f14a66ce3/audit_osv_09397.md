# [M] CVE-2016-9776

## Summary
Severity: Medium
Advisory: CVE-2016-9776
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9776
Type: osv

## Details
QEMU (aka Quick Emulator) built with the ColdFire Fast Ethernet Controller emulator support is vulnerable to an infinite loop issue. It could occur while receiving packets in 'mcf_fec_receive'. A privileged user/process inside guest could use this issue to crash the QEMU process on the host leading to DoS.

## References
- http://www.openwall.com/lists/oss-security/2016/12/02/3
- http://www.openwall.com/lists/oss-security/2016/12/02/8
- http://www.securityfocus.com/bid/94638
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201701-49
- https://bugzilla.redhat.com/show_bug.cgi?id=1400829
- https://lists.gnu.org/archive/html/qemu-devel/2016-11/msg05324.html
