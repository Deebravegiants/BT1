# [H] CVE-2017-7493

## Summary
Severity: High
Advisory: CVE-2017-7493
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-17
Source: https://osv.dev/vulnerability/CVE-2017-7493
Type: osv

## Details
Quick Emulator (Qemu) built with the VirtFS, host directory sharing via Plan 9 File System(9pfs) support, is vulnerable to an improper access control issue. It could occur while accessing virtfs metadata files in mapped-file security mode. A guest user could use this flaw to escalate their privileges inside guest.

## References
- http://www.securityfocus.com/bid/98574
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- http://seclists.org/oss-sec/2017/q2/278
- https://bugzilla.redhat.com/show_bug.cgi?id=1451709
- https://lists.gnu.org/archive/html/qemu-devel/2017-05/msg03663.html
