# [H] writeback: avoid use-after-free after removing device

## Summary
Severity: High
Advisory: CVE-2022-49995
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49995
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.64, >=5.16.0 <5.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

writeback: avoid use-after-free after removing device

When a disk is removed, bdi_unregister gets called to stop further
writeback and wait for associated delayed work to complete.  However,
wb_inode_writeback_end() may schedule bandwidth estimation dwork after
this has completed, which can result in the timer attempting to access the
just freed bdi_writeback.

Fix this by checking if the bdi_writeback is alive, similar to when
scheduling writeback work.

Since this requires wb->work_lock, and wb_inode_writeback_end() may get
called from interrupt, switch wb->work_lock to an irqsafe lock.

## References
- https://git.kernel.org/stable/c/9a6c710f3bc10bc9cc23e1c080b53245b7f9d5b7
- https://git.kernel.org/stable/c/f87904c075515f3e1d8f4a7115869d3b914674fd
- https://git.kernel.org/stable/c/f96b9f7c1676923bce871e728bb49c0dfa5013cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49995.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49995
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
