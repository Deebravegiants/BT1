# [H] CVE-2016-4805

## Summary
Severity: High
Advisory: CVE-2016-4805
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4805
Type: osv

## Details
Use-after-free vulnerability in drivers/net/ppp/ppp_generic.c in the Linux kernel before 4.5.2 allows local users to cause a denial of service (memory corruption and system crash, or spinlock) or possibly have unspecified other impact by removing a network namespace, related to the ppp_register_net_channel and ppp_unregister_channel functions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/90605
- http://www.securitytracker.com/id/1036763
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.debian.org/security/2016/dsa-3607
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.2
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.ubuntu.com/usn/USN-3021-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://www.ubuntu.com/usn/USN-3021-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1335803
- http://www.openwall.com/lists/oss-security/2016/05/15/2
- https://github.com/torvalds/linux/commit/1f461dcdd296eecedaffffc6bae2bfa90bd7eb89
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1f461dcdd296eecedaffffc6bae2bfa90bd7eb89
