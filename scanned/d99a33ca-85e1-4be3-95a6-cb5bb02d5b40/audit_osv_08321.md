# [M] CVE-2016-2198

## Summary
Severity: Medium
Advisory: CVE-2016-2198
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-2198
Type: osv

## Details
QEMU (aka Quick Emulator) built with the USB EHCI emulation support is vulnerable to a null pointer dereference flaw. It could occur when an application attempts to write to EHCI capabilities registers. A privileged user inside quest could use this flaw to crash the QEMU process instance resulting in DoS.

## References
- http://www.openwall.com/lists/oss-security/2016/01/29/6
- http://www.openwall.com/lists/oss-security/2016/01/30/2
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1301643
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg05899.html
