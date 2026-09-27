# [M] CVE-2017-5551

## Summary
Severity: Medium
Advisory: CVE-2017-5551
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5551
Type: osv

## Details
The simple_set_acl function in fs/posix_acl.c in the Linux kernel before 4.9.6 preserves the setgid bit during a setxattr call involving a tmpfs filesystem, which allows local users to gain group privileges by leveraging the existence of a setgid program with restrictions on execute permissions.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-7097.

## References
- http://www.securitytracker.com/id/1038053
- http://www.debian.org/security/2017/dsa-3791
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6
- http://www.securityfocus.com/bid/95717
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=497de07d89c1410d76a15bec2bb41f24a2a89f31
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416126
- https://github.com/torvalds/linux/commit/497de07d89c1410d76a15bec2bb41f24a2a89f31
