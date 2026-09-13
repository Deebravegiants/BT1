# [H] CVE-2018-15664

## Summary
Severity: High
Advisory: CVE-2018-15664
CVSS: 7.5 (CVSS:3.0/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2018-15664
Type: osv

## Details
In Docker through 18.06.1-ce-rc2, the API endpoints behind the 'docker cp' command are vulnerable to a symlink-exchange attack with Directory Traversal, giving attackers arbitrary read-write access to the host filesystem with root privileges, because daemon/archive.go does not do archive operations on a frozen filesystem (or from within a chroot).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00066.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00001.html
- http://www.openwall.com/lists/oss-security/2019/08/21/1
- https://usn.ubuntu.com/4048-1/
- http://www.securityfocus.com/bid/108507
- https://access.redhat.com/errata/RHSA-2019:1910
- https://access.redhat.com/security/cve/cve-2018-15664
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-15664
- https://bugzilla.suse.com/show_bug.cgi?id=1096726
- https://github.com/moby/moby/pull/39252
- http://www.openwall.com/lists/oss-security/2019/05/28/1
