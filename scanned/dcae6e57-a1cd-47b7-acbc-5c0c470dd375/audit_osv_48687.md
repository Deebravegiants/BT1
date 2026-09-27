# [M] CVE-2018-1120

## Summary
Severity: Medium
Advisory: CVE-2018-1120
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/CVE-2018-1120
Type: osv

## Details
A flaw was found affecting the Linux kernel before version 4.17. By mmap()ing a FUSE-backed file onto a process's memory containing command line arguments (or environment strings), an attacker can cause utilities from psutils or procps (such as ps, w) or any other program which makes a read() call to the /proc/<pid>/cmdline (or /proc/<pid>/environ) files to block indefinitely (denial of service) or for some controlled time (as a synchronization primitive for other attacks).

## References
- https://usn.ubuntu.com/3910-1/
- https://usn.ubuntu.com/3910-2/
- http://www.securityfocus.com/bid/104229
- https://access.redhat.com/errata/RHSA-2018:3096
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3752-2/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://security.gentoo.org/glsa/201805-14
- https://access.redhat.com/errata/RHSA-2018:3083
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7f7ccc2ccc2e70c6054685f5e3522efa81556830
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1120
- http://seclists.org/oss-sec/2018/q2/122
- https://www.exploit-db.com/exploits/44806/
