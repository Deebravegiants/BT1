# [H] workqueue: Put the pwq after detaching the rescuer from the pool

## Summary
Severity: High
Advisory: CVE-2025-21786
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21786
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

workqueue: Put the pwq after detaching the rescuer from the pool

The commit 68f83057b913("workqueue: Reap workers via kthread_stop() and
remove detach_completion") adds code to reap the normal workers but
mistakenly does not handle the rescuer and also removes the code waiting
for the rescuer in put_unbound_pool(), which caused a use-after-free bug
reported by Cheung Wall.

To avoid the use-after-free bug, the pool’s reference must be held until
the detachment is complete. Therefore, move the code that puts the pwq
after detaching the rescuer from the pool.

## References
- https://git.kernel.org/stable/c/835b69c868f53f959d4986bbecd561ba6f38e492
- https://git.kernel.org/stable/c/e76946110137703c16423baf6ee177b751a34b7e
- https://git.kernel.org/stable/c/e7c16028a424dd35be1064a68fa318be4359310f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21786.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21786
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
