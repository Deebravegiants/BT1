# [M] CVE-2013-4312

## Summary
Severity: Medium
Advisory: CVE-2013-4312
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2013-4312
Type: osv

## Details
The Linux kernel before 4.4.1 allows local users to bypass file-descriptor limits and cause a denial of service (memory consumption) by sending each descriptor over a UNIX socket before closing it, related to net/unix/af_unix.c and net/unix/garbage.c.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=712f4aad406bb1ed67f3f98d04c044191f0ff593
- http://rhn.redhat.com/errata/RHSA-2016-0855.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.debian.org/security/2016/dsa-3448
- http://www.debian.org/security/2016/dsa-3503
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2931-1
- http://www.ubuntu.com/usn/USN-2932-1
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1297813
- https://github.com/torvalds/linux/commit/712f4aad406bb1ed67f3f98d04c044191f0ff593
- https://security-tracker.debian.org/tracker/CVE-2013-4312
- https://bugzilla.redhat.com/show_bug.cgi?id=1297813
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176464.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
