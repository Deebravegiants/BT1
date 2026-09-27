# [M] f2fs: initialize locks earlier in f2fs_fill_super()

## Summary
Severity: Medium
Advisory: CVE-2022-49742
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49742
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: initialize locks earlier in f2fs_fill_super()

syzbot is reporting lockdep warning at f2fs_handle_error() [1], for
spin_lock(&sbi->error_lock) is called before spin_lock_init() is called.
For safe locking in error handling, move initialization of locks (and
obvious structures) in f2fs_fill_super() to immediately after memory
allocation.

## References
- https://git.kernel.org/stable/c/92b4cf5b48955a4bdd15fe4e2067db8ebd87f04c
- https://git.kernel.org/stable/c/ddeff03bb33810fcf2f0c18e03d099cf0aacda62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49742.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
