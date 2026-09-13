# [H] CVE-2015-8709

## Summary
Severity: High
Advisory: CVE-2015-8709
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2015-8709
Type: osv

## Details
kernel/ptrace.c in the Linux kernel through 4.4.1 mishandles uid and gid mappings, which allows local users to gain privileges by establishing a user namespace, waiting for a root process to enter that namespace with an unsafe uid or gid, and then using the ptrace system call.  NOTE: the vendor states "there is no kernel bug here.

## References
- http://www.debian.org/security/2016/dsa-3434
- https://bugzilla.redhat.com/show_bug.cgi?id=1295287
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://marc.info/?l=linux-kernel&m=145204362722256&w=2
- http://marc.info/?l=linux-kernel&m=145204641422813&w=2
