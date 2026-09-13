# [H] nilfs2: fix data corruption in dsync block recovery for small block sizes

## Summary
Severity: High
Advisory: CVE-2024-26697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26697
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix data corruption in dsync block recovery for small block sizes

The helper function nilfs_recovery_copy_block() of
nilfs_recovery_dsync_blocks(), which recovers data from logs created by
data sync writes during a mount after an unclean shutdown, incorrectly
calculates the on-page offset when copying repair data to the file's page
cache.  In environments where the block size is smaller than the page
size, this flaw can cause data corruption and leak uninitialized memory
bytes during the recovery process.

Fix these issues by correcting this byte offset calculation on the page.

## References
- https://git.kernel.org/stable/c/120f7fa2008e3bd8b7680b4ab5df942decf60fd5
- https://git.kernel.org/stable/c/2000016bab499074e6248ea85aeea7dd762355d9
- https://git.kernel.org/stable/c/2e1480538ef60bfee5473dfe02b1ecbaf1a4aa0d
- https://git.kernel.org/stable/c/364a66be2abdcd4fd426ffa44d9b8f40aafb3caa
- https://git.kernel.org/stable/c/5278c3eb6bf5896417572b52adb6be9d26e92f65
- https://git.kernel.org/stable/c/67b8bcbaed4777871bb0dcc888fb02a614a98ab1
- https://git.kernel.org/stable/c/9c9c68d64fd3284f7097ed6ae057c8441f39fcd3
- https://git.kernel.org/stable/c/a6efe6dbaaf504f5b3f8a5c3f711fe54e7dda0ba
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26697.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
