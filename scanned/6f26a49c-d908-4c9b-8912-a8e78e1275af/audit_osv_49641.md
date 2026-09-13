# [M] CVE-2019-15030

## Summary
Severity: Medium
Advisory: CVE-2019-15030
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-09-13
Source: https://osv.dev/vulnerability/CVE-2019-15030
Type: osv

## Details
In the Linux kernel through 5.2.14 on the powerpc platform, a local user can read vector registers of other users' processes via a Facility Unavailable exception. To exploit the venerability, a local user starts a transaction (via the hardware transactional memory instruction tbegin) and then accesses vector registers. At some point, the vector registers will be corrupted with the values from a different local Linux process because of a missing arch/powerpc/kernel/process.c check.

## References
- https://usn.ubuntu.com/4135-1/
- https://usn.ubuntu.com/4135-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://access.redhat.com/errata/RHSA-2020:0740
- https://security.netapp.com/advisory/ntap-20191004-0001/
- http://www.openwall.com/lists/oss-security/2019/09/10/3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8205d5d98ef7f155de211f5e2eb6ca03d95a5a60
