# [M] quota: flush quota_release_work upon quota writeback

## Summary
Severity: Medium
Advisory: CVE-2024-56780
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56780
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.6.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

quota: flush quota_release_work upon quota writeback

One of the paths quota writeback is called from is:

freeze_super()
  sync_filesystem()
    ext4_sync_fs()
      dquot_writeback_dquots()

Since we currently don't always flush the quota_release_work queue in
this path, we can end up with the following race:

 1. dquot are added to releasing_dquots list during regular operations.
 2. FS Freeze starts, however, this does not flush the quota_release_work queue.
 3. Freeze completes.
 4. Kernel eventually tries to flush the workqueue while FS is frozen which
    hits a WARN_ON since transaction gets started during frozen state:

  ext4_journal_check_start+0x28/0x110 [ext4] (unreliable)
  __ext4_journal_start_sb+0x64/0x1c0 [ext4]
  ext4_release_dquot+0x90/0x1d0 [ext4]
  quota_release_workfn+0x43c/0x4d0

Which is the following line:

  WARN_ON(sb->s_writers.frozen == SB_FREEZE_COMPLETE);

Which ultimately results in generic/390 failing due to dmesg
noise. This was detected on powerpc machine 15 cores.

To avoid this, make sure to flush the workqueue during
dquot_writeback_dquots() so we dont have any pending workitems after
freeze.

## References
- https://git.kernel.org/stable/c/3e6ff207cd5bd924ad94cd1a7c633bcdac0ba1cb
- https://git.kernel.org/stable/c/6f3821acd7c3143145999248087de5fb4b48cf26
- https://git.kernel.org/stable/c/8ea87e34792258825d290f4dc5216276e91cb224
- https://git.kernel.org/stable/c/a5abba5e0e586e258ded3e798fe5f69c66fec198
- https://git.kernel.org/stable/c/ab6cfcf8ed2c7496f55d020b65b1d8cd55d9a2cb
- https://git.kernel.org/stable/c/ac6f420291b3fee1113f21d612fa88b628afab5b
- https://git.kernel.org/stable/c/bcacb52a985f1b6d280f698a470b873dfe52728a
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56780.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
