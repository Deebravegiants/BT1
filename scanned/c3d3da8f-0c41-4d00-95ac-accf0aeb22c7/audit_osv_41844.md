# [H] dpll: zl3073x: use __dpll_device_change_ntf() and remove change_work

## Summary
Severity: High
Advisory: CVE-2026-63977
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63977
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

dpll: zl3073x: use __dpll_device_change_ntf() and remove change_work

The change_work was introduced to send device change notifications
from DPLL device callbacks without deadlocking on dpll_lock, since
the callbacks are already invoked under that lock. Now that
__dpll_device_change_ntf() is exported for callers that already
hold dpll_lock, use it directly and remove the change_work
infrastructure entirely.

This eliminates a race condition where change_work could be
re-scheduled after cancel_work_sync() during device teardown,
potentially causing the handler to dereference a freed or NULL
dpll_dev pointer.

## References
- https://git.kernel.org/stable/c/d733f519f6443540f8359461a34e3b0042099bbe
- https://git.kernel.org/stable/c/e7a33807fb3f87a855993474ac21684ce105927b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63977.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
