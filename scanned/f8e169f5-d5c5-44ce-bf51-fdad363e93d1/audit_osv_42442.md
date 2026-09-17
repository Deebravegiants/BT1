# [H] amt: fix use-after-free in AMT delayed works

## Summary
Severity: High
Advisory: CVE-2026-68152
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68152
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

amt: fix use-after-free in AMT delayed works

When an AMT device is removed, pending delayed works can still access
the freed amt_dev structure, which may result in kernel crashes or
memory corruption.

amt_dev_stop() cancels req_wq and discovery_wq with
cancel_delayed_work_sync(), but these works can be scheduled again
from event_wq after the cancellation. This allows delayed works to
access the freed amt_dev structure after the netdev has been released.

The following is a simple race scenario:

CPU0                         CPU1

amt_dev_stop()
cancel_delayed_work_sync()
                             amt_event_work()
                             mod_delayed_work(req_wq)
free netdev
                             req_wq accesses freed amt_dev

Use disable_delayed_work_sync() in amt_dev_stop() to prevent req_wq and
discovery_wq from being queued again and wait for running work items
to complete.

The delayed works are disabled after initialization in
amt_newlink() and enabled only when the device is successfully opened.
This keeps the delayed work lifecycle synchronized with the lifetime
of the AMT device.

## References
- https://git.kernel.org/stable/c/006340cf06881b6ff49767d8b6f3c4f7b892670c
- https://git.kernel.org/stable/c/1a644db2cf59f164cdf3c75995bab5aadc097528
- https://git.kernel.org/stable/c/a46bfa01e01df0f6f6dc4b0be18db002d6d2dbd2
- https://git.kernel.org/stable/c/ea20c44935d6142daecfa9b39d635033a7553e1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68152.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68152
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
