# [M] CVE-2016-7097

## Summary
Severity: Medium
Advisory: CVE-2016-7097
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-7097
Type: osv

## Details
The filesystem implementation in the Linux kernel through 4.8.2 preserves the setgid bit during a setxattr call, which allows local users to gain group privileges by leveraging the existence of a setgid program with restrictions on execute permissions.

## References
- https://support.f5.com/csp/article/K31603170?utm_source=f5support&amp%3Butm_medium=RSS
- https://source.android.com/security/bulletin/2017-04-01
- http://www.securitytracker.com/id/1038201
- http://www.securityfocus.com/bid/92659
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.ubuntu.com/usn/USN-3146-1
- http://www.ubuntu.com/usn/USN-3146-2
- http://rhn.redhat.com/errata/RHSA-2017-0817.html
- http://www.ubuntu.com/usn/USN-3147-1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://bugzilla.redhat.com/show_bug.cgi?id=1368938
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=073931017b49d9458aa351605b43a7e34598caef
- https://github.com/torvalds/linux/commit/073931017b49d9458aa351605b43a7e34598caef
- http://marc.info/?l=linux-fsdevel&m=147162313630259&w=2
- http://www.spinics.net/lists/linux-fsdevel/msg98328.html
- http://www.openwall.com/lists/oss-security/2016/08/26/3
