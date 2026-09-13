# [M] CVE-2019-15214

## Summary
Severity: Medium
Advisory: CVE-2019-15214
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15214
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.10. There is a use-after-free in the sound subsystem because card disconnection causes certain data structures to be deleted too early. This is related to sound/core/init.c and sound/core/info.c.

## References
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://usn.ubuntu.com/4115-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8c2f870890fd28e023b0fcf49dcee333f2c8bad7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2a3f7221acddfe1caa9ff09b3a8158c39b2fdeac
- https://syzkaller.appspot.com/bug?id=75903e0021cef79bc434d068b5169b599b2a46a9
