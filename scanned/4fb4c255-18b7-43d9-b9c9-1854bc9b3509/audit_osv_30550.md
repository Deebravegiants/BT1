# [H] fsnotify: Fix ordering of iput() and watched_objects decrement

## Summary
Severity: High
Advisory: CVE-2024-53143
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-07
Source: https://osv.dev/vulnerability/CVE-2024-53143
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fsnotify: Fix ordering of iput() and watched_objects decrement

Ensure the superblock is kept alive until we're done with iput().
Holding a reference to an inode is not allowed unless we ensure the
superblock stays alive, which fsnotify does by keeping the
watched_objects count elevated, so iput() must happen before the
watched_objects decrement.
This can lead to a UAF of something like sb->s_fs_info in tmpfs, but the
UAF is hard to hit because race orderings that oops are more likely, thanks
to the CHECK_DATA_CORRUPTION() block in generic_shutdown_super().

Also, ensure that fsnotify_put_sb_watched_objects() doesn't call
fsnotify_sb_watched_objects() on a superblock that may have already been
freed, which would cause a UAF read of sb->s_fsnotify_info.

## References
- https://git.kernel.org/stable/c/21d1b618b6b9da46c5116c640ac4b1cc8d40d63a
- https://git.kernel.org/stable/c/45a8f8232a495221ed058191629f5c628f21601a
- https://git.kernel.org/stable/c/83af1cfa10d9aafdabd06b3655e07727f373b434
- https://project-zero.issues.chromium.org/issues/379667898
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53143.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53143
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
