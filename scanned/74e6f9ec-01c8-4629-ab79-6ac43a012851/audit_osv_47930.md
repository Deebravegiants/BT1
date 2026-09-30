# [H] CVE-2017-15115

## Summary
Severity: High
Advisory: CVE-2017-15115
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-15115
Type: osv

## Details
The sctp_do_peeloff function in net/sctp/socket.c in the Linux kernel before 4.14 does not check whether the intended netns is used in a peel-off action, which allows local users to cause a denial of service (use-after-free and system crash) or possibly have unspecified other impact via crafted system calls.

## References
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3581-1/
- https://usn.ubuntu.com/3581-3/
- https://source.android.com/security/bulletin/pixel/2018-04-01
- https://usn.ubuntu.com/3581-2/
- https://usn.ubuntu.com/3582-2/
- https://usn.ubuntu.com/3583-1/
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://www.securityfocus.com/bid/101877
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3582-1/
- http://seclists.org/oss-sec/2017/q4/282
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=df80cd9b28b9ebaa284a41df611dbf3a2d05ca74
- https://bugzilla.redhat.com/show_bug.cgi?id=1513345
- https://github.com/torvalds/linux/commit/df80cd9b28b9ebaa284a41df611dbf3a2d05ca74
- https://patchwork.ozlabs.org/patch/827077/
