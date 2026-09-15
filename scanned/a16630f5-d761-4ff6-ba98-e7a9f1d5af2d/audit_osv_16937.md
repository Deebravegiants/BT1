# [H] CVE-2020-10757

## Summary
Severity: High
Advisory: CVE-2020-10757
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-10757
Type: osv

## Details
A flaw was found in the Linux Kernel in versions after 4.5-rc1 in the way mremap handled DAX Huge Pages. This flaw allows a local attacker with access to a DAX enabled storage to escalate their privileges on the system.

## References
- https://www.debian.org/security/2020/dsa-4699
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IEM47BXZJLODRH5YNNZSAQ2NVM63MYMC/
- https://security.netapp.com/advisory/ntap-20200702-0004/
- https://usn.ubuntu.com/4440-1/
- https://usn.ubuntu.com/4426-1/
- https://usn.ubuntu.com/4439-1/
- https://usn.ubuntu.com/4483-1/
- https://www.debian.org/security/2020/dsa-4698
- https://bugzilla.redhat.com/show_bug.cgi?id=1842525
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5bfea2d9b17f1034a68147a8b03b9789af5700f9
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://www.openwall.com/lists/oss-security/2020/06/04/4
