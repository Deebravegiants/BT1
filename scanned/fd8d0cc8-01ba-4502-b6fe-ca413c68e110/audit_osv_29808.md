# [H] libfs: fix get_stashed_dentry()

## Summary
Severity: High
Advisory: CVE-2024-46801
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46801
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libfs: fix get_stashed_dentry()

get_stashed_dentry() tries to optimistically retrieve a stashed dentry
from a provided location.  It needs to ensure to hold rcu lock before it
dereference the stashed location to prevent UAF issues.  Use
rcu_dereference() instead of READ_ONCE() it's effectively equivalent
with some lockdep bells and whistles and it communicates clearly that
this expects rcu protection.

## References
- https://git.kernel.org/stable/c/03e2a1209a83a380df34a72f7d6d1bc6c74132c7
- https://git.kernel.org/stable/c/4e32c25b58b945f976435bbe51f39b32d714052e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46801.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
