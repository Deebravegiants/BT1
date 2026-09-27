# [H] CVE-2020-8428

## Summary
Severity: High
Advisory: CVE-2020-8428
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/CVE-2020-8428
Type: osv

## Details
fs/namei.c in the Linux kernel before 5.5 has a may_create_in_sticky use-after-free, which allows local users to cause a denial of service (OOPS) or possibly obtain sensitive information from kernel memory, aka CID-d0cb50185ae9. One attack vector may be an open system call for a UNIX domain socket, if the socket is being moved to a new parent directory and its old parent directory is being removed.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://usn.ubuntu.com/4318-1/
- https://usn.ubuntu.com/4319-1/
- https://usn.ubuntu.com/4320-1/
- https://usn.ubuntu.com/4324-1/
- http://www.openwall.com/lists/oss-security/2020/02/02/1
- http://packetstormsecurity.com/files/157233/Kernel-Live-Patch-Security-Notice-LSN-0065-1.html
- https://usn.ubuntu.com/4325-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://www.debian.org/security/2020/dsa-4667
- http://www.openwall.com/lists/oss-security/2020/01/28/4
- https://security.netapp.com/advisory/ntap-20200313-0003/
- https://www.debian.org/security/2020/dsa-4698
- https://www.openwall.com/lists/oss-security/2020/01/28/2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d0cb50185ae942b03c4327be322055d622dc79f6
- https://github.com/torvalds/linux/commit/d0cb50185ae942b03c4327be322055d622dc79f6
