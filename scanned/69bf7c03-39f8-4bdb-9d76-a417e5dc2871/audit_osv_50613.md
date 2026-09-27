# [H] CVE-2020-25668

## Summary
Severity: High
Advisory: CVE-2020-25668
Aliases: A-190228658, PUB-A-190228658
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-25668
Type: osv

## Details
A flaw was found in Linux Kernel because access to the global variable fg_console is not properly synchronized leading to a use after free in con_font_op.

## References
- https://www.openwall.com/lists/oss-security/2020/10/30/1%2C
- https://www.openwall.com/lists/oss-security/2020/11/04/3%2C
- https://security.netapp.com/advisory/ntap-20210702-0005/
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1893287%2C
- http://www.openwall.com/lists/oss-security/2020/10/30/1
- http://www.openwall.com/lists/oss-security/2020/11/04/3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=90bfdeef83f1d6c696039b6a917190dcbbad3220
