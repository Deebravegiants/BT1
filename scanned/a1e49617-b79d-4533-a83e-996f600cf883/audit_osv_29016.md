# [H] blk-cgroup: fix list corruption from resetting io stat

## Summary
Severity: High
Advisory: CVE-2024-38663
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-38663
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: fix list corruption from resetting io stat

Since commit 3b8cc6298724 ("blk-cgroup: Optimize blkcg_rstat_flush()"),
each iostat instance is added to blkcg percpu list, so blkcg_reset_stats()
can't reset the stat instance by memset(), otherwise the llist may be
corrupted.

Fix the issue by only resetting the counter part.

## References
- https://git.kernel.org/stable/c/6da6680632792709cecf2b006f2fe3ca7857e791
- https://git.kernel.org/stable/c/89bb36c72e1951843f9e04dc84412e31fcc849a9
- https://git.kernel.org/stable/c/d4a60298ac34f027a09f8f893fdbd9e06279bb24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38663.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38663
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
