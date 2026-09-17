# [M] CVE-2019-15031

## Summary
Severity: Medium
Advisory: CVE-2019-15031
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-09-13
Source: https://osv.dev/vulnerability/CVE-2019-15031
Type: osv

## Details
In the Linux kernel through 5.2.14 on the powerpc platform, a local user can read vector registers of other users' processes via an interrupt. To exploit the venerability, a local user starts a transaction (via the hardware transactional memory instruction tbegin) and then accesses vector registers. At some point, the vector registers will be corrupted with the values from a different local Linux process, because MSR_TM_ACTIVE is misused in arch/powerpc/kernel/process.c.

## References
- https://usn.ubuntu.com/4135-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4135-1/
- http://www.openwall.com/lists/oss-security/2019/09/10/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a8318c13e79badb92bc6640704a64cc022a6eb97
