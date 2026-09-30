# [H] RDMA/nldev: Fix locking when accessing mr->pd

## Summary
Severity: High
Advisory: CVE-2026-74334
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74334
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/nldev: Fix locking when accessing mr->pd

Sashiko points out that, due to rereg_mr, the PD is actually variable and
all the touches in nldev are racy.

Use mr->device instead of mr->pd->device.

Getting the PD restrack ID is more tricky. To avoid disturbing all the
happy paths, add an rdma_restrack_sync() operation which is sort of like
flush_workqueue() or synchronize_irq(): after it returns, all the old
nldev touches to the mr are gone and everything sees the new PD. This
makes it safe to reach into the PD pointer.

## References
- https://git.kernel.org/stable/c/1a132ee4e655288d9a0937ea5109a0d038431ae9
- https://git.kernel.org/stable/c/50d5c02ab8e62325548bd3a6e6b758a9dcd6e7c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74334.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74334
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
