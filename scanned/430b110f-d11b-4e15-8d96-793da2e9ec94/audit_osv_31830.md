# [M] drm/i915/gt: Use spin_lock_irqsave() in interruptible context

## Summary
Severity: Medium
Advisory: CVE-2025-21849
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21849
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/gt: Use spin_lock_irqsave() in interruptible context

spin_lock/unlock() functions used in interrupt contexts could
result in a deadlock, as seen in GitLab issue #13399,
which occurs when interrupt comes in while holding a lock.

Try to remedy the problem by saving irq state before spin lock
acquisition.

v2: add irqs' state save/restore calls to all locks/unlocks in
 signal_irq_work() execution (Maciej)

v3: use with spin_lock_irqsave() in guc_lrc_desc_unpin() instead
 of other lock/unlock calls and add Fixes and Cc tags (Tvrtko);
 change title and commit message

(cherry picked from commit c088387ddd6482b40f21ccf23db1125e8fa4af7e)

## References
- https://git.kernel.org/stable/c/2bf1f4c129db7a10920655b000f0292f1ee509c2
- https://git.kernel.org/stable/c/47ae46ac5407646420e06b78e0dad331e56a4bb4
- https://git.kernel.org/stable/c/e49477f7f78598295551d486ecc7f020d796432e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21849.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21849
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
