# [H] iommu/amd: Wait for completion instead of returning early in iommu_completion_wait()

## Summary
Severity: High
Advisory: CVE-2026-68329
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68329
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/amd: Wait for completion instead of returning early in iommu_completion_wait()

need_sync is a per-IOMMU flag shared by all domains and devices behind
that IOMMU. It is set whenever a command is queued with sync == true and
cleared when a completion-wait (CWAIT) command is queued. However, a
cleared need_sync only means that a covering CWAIT has been queued, not
that all previously queued commands have actually completed in hardware.

iommu_completion_wait() read need_sync locklessly and returned early
when it was false. This breaks the "block until all previously queued
commands have completed" contract in a multi-CPU scenario:

  CPU2: queue inv-B                  => need_sync = true
  CPU1: queue CWAIT(N); need_sync = false; then wait_on_sem(N)
  CPU2: read need_sync == false      => return 0 (no wait!)

CPU2 returns without waiting for any sequence number even though its
inv-B may not have completed yet (CWAIT(N), queued after inv-B, has not
been signaled). CPU2 then proceeds to, for example, free page-table
pages while the IOMMU can still walk stale translations, opening a
use-after-free window. This is a logical race in the meaning of the
flag, not a memory-visibility issue, so barriers alone do not help.

Fix it without losing the optimization of avoiding redundant CWAIT
commands: take iommu->lock before testing need_sync, and when it is
false do not return early but wait for the last allocated sequence
number (cmd_sem_val). Since need_sync == false implies no sync command
was queued after the last CWAIT, that CWAIT is FIFO-ordered after every
not-yet-completed command, so waiting for its sequence number guarantees
all prior commands (possibly queued by another CPU) have completed. The
common path with pending work is unchanged and no extra hardware command
is issued.

## References
- https://git.kernel.org/stable/c/02f8cefa2ad95ea3754f0cfd6fbae7f866202ccb
- https://git.kernel.org/stable/c/1e75a8255f11c81fb07e81e5029cfd75804350a0
- https://git.kernel.org/stable/c/93494bd446396c257fb589f59894577e96e406e2
- https://git.kernel.org/stable/c/ab7faf5a172ebfdc423ebb3eea4d472740de82f9
- https://git.kernel.org/stable/c/d053eb7e09e10cbdca3fca8b35c1017d438091b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68329.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
