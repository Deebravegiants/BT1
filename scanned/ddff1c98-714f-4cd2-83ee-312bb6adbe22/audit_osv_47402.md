# [M] CVE-2016-4581

## Summary
Severity: Medium
Advisory: CVE-2016-4581
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4581
Type: osv

## Details
fs/pnode.c in the Linux kernel before 4.5.4 does not properly traverse a mount propagation tree in a certain case involving a slave mount, which allows local users to cause a denial of service (NULL pointer dereference and OOPS) via a crafted series of mount system calls.

## References
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.securityfocus.com/bid/90607
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5ec0811d30378ae104f250bfc9b3640242d81e3f
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.openwall.com/lists/oss-security/2016/05/11/2
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2998-1
- http://www.ubuntu.com/usn/USN-3003-1
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.ubuntu.com/usn/USN-3001-1
- http://www.ubuntu.com/usn/USN-3002-1
- http://www.ubuntu.com/usn/USN-3005-1
- http://www.ubuntu.com/usn/USN-3007-1
- http://www.ubuntu.com/usn/USN-3000-1
- http://www.ubuntu.com/usn/USN-3004-1
- https://github.com/torvalds/linux/commit/5ec0811d30378ae104f250bfc9b3640242d81e3f
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.ubuntu.com/usn/USN-2989-1
