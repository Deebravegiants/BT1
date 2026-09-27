# [H] CVE-2016-10153

## Summary
Severity: High
Advisory: CVE-2016-10153
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-10153
Type: osv

## Details
The crypto scatterlist API in the Linux kernel 4.9.x before 4.9.6 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging reliance on earlier net/ceph/crypto.c code.

## References
- http://www.securityfocus.com/bid/95713
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416101
- https://github.com/torvalds/linux/commit/a45f795c65b479b4ba107b6ccde29b896d51ee98
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a45f795c65b479b4ba107b6ccde29b896d51ee98
