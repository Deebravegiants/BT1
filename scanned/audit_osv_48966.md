# [H] CVE-2018-18955

## Summary
Severity: High
Advisory: CVE-2018-18955
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-16
Source: https://osv.dev/vulnerability/CVE-2018-18955
Type: osv

## Details
In the Linux kernel 4.15.x through 4.19.x before 4.19.2, map_write() in kernel/user_namespace.c allows privilege escalation because it mishandles nested user namespaces with more than 5 UID or GID ranges. A user who has CAP_SYS_ADMIN in an affected user namespace can bypass access controls on resources outside the namespace, as demonstrated by reading /etc/shadow. This occurs because an ID transformation takes place properly for the namespaced-to-kernel direction but not for the kernel-to-namespaced direction.

## References
- https://support.f5.com/csp/article/K39103040
- https://security.netapp.com/advisory/ntap-20190416-0003/
- https://usn.ubuntu.com/3836-2/
- http://www.securityfocus.com/bid/105941
- https://usn.ubuntu.com/3832-1/
- https://usn.ubuntu.com/3833-1/
- https://usn.ubuntu.com/3835-1/
- https://usn.ubuntu.com/3836-1/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.2
- https://github.com/torvalds/linux/commit/d2f007dbe7e4c9583eea6eb04d60001e85c6f1bd
- https://www.exploit-db.com/exploits/45886/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1712
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d2f007dbe7e4c9583eea6eb04d60001e85c6f1bd
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.19
- https://www.exploit-db.com/exploits/45915/
