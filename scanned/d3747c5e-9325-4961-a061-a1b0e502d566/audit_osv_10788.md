# [H] CVE-2017-2630

## Summary
Severity: High
Advisory: CVE-2017-2630
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2630
Type: osv

## Details
A stack buffer overflow flaw was found in the Quick Emulator (QEMU) before 2.9 built with the Network Block Device (NBD) client support. The flaw could occur while processing server's response to a 'NBD_OPT_LIST' request. A malicious NBD server could use this issue to crash a remote NBD client resulting in DoS or potentially execute arbitrary code on client host with privileges of the QEMU process.

## References
- http://www.securityfocus.com/bid/96265
- https://access.redhat.com/errata/RHSA-2017:2392
- https://security.gentoo.org/glsa/201704-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1422415
- http://www.openwall.com/lists/oss-security/2017/02/15/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2630
- https://github.com/qemu/qemu/commit/2563c9c6b8670400c48e562034b321a7cf3d9a85
- https://lists.gnu.org/archive/html/qemu-devel/2017-02/msg01246.html
