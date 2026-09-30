# [M] ksmbd: fix reference count leak in smb_check_perm_dacl()

## Summary
Severity: Medium
Advisory: CVE-2022-49366
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49366
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix reference count leak in smb_check_perm_dacl()

The issue happens in a specific path in smb_check_perm_dacl(). When
"id" and "uid" have the same value, the function simply jumps out of
the loop without decrementing the reference count of the object
"posix_acls", which is increased by get_acl() earlier. This may
result in memory leaks.

Fix it by decreasing the reference count of "posix_acls" before
jumping to label "check_access_bits".

## References
- https://git.kernel.org/stable/c/248d71b440aef829f5cc5f6545ca113ef5062900
- https://git.kernel.org/stable/c/9758a6653c27867d810de02b4e5697163dda9883
- https://git.kernel.org/stable/c/cf824b95c12a1abacadbc2d069931963221a3414
- https://git.kernel.org/stable/c/d21a580dafc69aa04f46e6099616146a536b0724
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49366.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
