# [H] jfs: add check read-only before truncation in jfs_truncate_nolock()

## Summary
Severity: High
Advisory: CVE-2024-58094
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2024-58094
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.269, >=5.11.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: add check read-only before truncation in jfs_truncate_nolock()

Added a check for "read-only" mode in the `jfs_truncate_nolock`
function to avoid errors related to writing to a read-only
filesystem.

Call stack:

block_write_begin() {
  jfs_write_failed() {
    jfs_truncate() {
      jfs_truncate_nolock() {
        txEnd() {
          ...
          log = JFS_SBI(tblk->sb)->log;
          // (log == NULL)

If the `isReadOnly(ip)` condition is triggered in
`jfs_truncate_nolock`, the function execution will stop, and no
further data modification will occur. Instead, the `xtTruncate`
function will be called with the "COMMIT_WMAP" flag, preventing
modifications in "read-only" mode.

## References
- https://git.kernel.org/stable/c/1fee021d6cf1d41b3f6e3fd028939be8f5d5c5db
- https://git.kernel.org/stable/c/41da1715cd24e177678f93ee27f737b095fc838b
- https://git.kernel.org/stable/c/77038187890ea82d237b05c8a9c4e08a38b1efcb
- https://git.kernel.org/stable/c/b5799dd77054c1ec49b0088b006c9908e256843b
- https://git.kernel.org/stable/c/b57a8983916fc2cf54fd8de3afc733c6b3d1c0e5
- https://git.kernel.org/stable/c/b98506e61e1bb6764c6711198cfab826df8ca952
- https://git.kernel.org/stable/c/f605bc3e162f5c6faa9bd3602ce496053d06a4bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58094.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
