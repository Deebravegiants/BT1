# [H] thermal: core: Address thermal zone removal races with resume

## Summary
Severity: High
Advisory: CVE-2026-31731
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31731
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.83, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: core: Address thermal zone removal races with resume

Since thermal_zone_pm_complete() and thermal_zone_device_resume()
re-initialize the poll_queue delayed work for the given thermal zone,
the cancel_delayed_work_sync() in thermal_zone_device_unregister()
may miss some already running work items and the thermal zone may
be freed prematurely [1].

There are two failing scenarios that both start with
running thermal_pm_notify_complete() right before invoking
thermal_zone_device_unregister() for one of the thermal zones.

In the first scenario, there is a work item already running for
the given thermal zone when thermal_pm_notify_complete() calls
thermal_zone_pm_complete() for that thermal zone and it continues to
run when thermal_zone_device_unregister() starts.  Since the poll_queue
delayed work has been re-initialized by thermal_pm_notify_complete(), the
running work item will be missed by the cancel_delayed_work_sync() in
thermal_zone_device_unregister() and if it continues to run past the
freeing of the thermal zone object, a use-after-free will occur.

In the second scenario, thermal_zone_device_resume() queued up by
thermal_pm_notify_complete() runs right after the thermal_zone_exit()
called by thermal_zone_device_unregister() has returned.  The poll_queue
delayed work is re-initialized by it before cancel_delayed_work_sync() is
called by thermal_zone_device_unregister(), so it may continue to run
after the freeing of the thermal zone object, which also leads to a
use-after-free.

Address the first failing scenario by ensuring that no thermal work
items will be running when thermal_pm_notify_complete() is called.
For this purpose, first move the cancel_delayed_work() call from
thermal_zone_pm_complete() to thermal_zone_pm_prepare() to prevent
new work from entering the workqueue going forward.  Next, switch
over to using a dedicated workqueue for thermal events and update
the code in thermal_pm_notify() to flush that workqueue after
thermal_pm_notify_prepare() has returned which will take care of
all leftover thermal work already on the workqueue (that leftover
work would do nothing useful anyway because all of the thermal zones
have been flagged as suspended).

The second failing scenario is addressed by adding a tz->state check
to thermal_zone_device_resume() to prevent it from re-initializing
the poll_queue delayed work if the thermal zone is going away.

Note that the above changes will also facilitate relocating the suspend
and resume of thermal zones closer to the suspend and resume of devices,
respectively.

## References
- https://git.kernel.org/stable/c/1a6d2b001eb730d85f00da39ae7db6f3b4edc540
- https://git.kernel.org/stable/c/2dbe93f344f10b432b95a23304006be805c097a1
- https://git.kernel.org/stable/c/45b859b0728267a6199ee5002d62e6c6f3e8c89d
- https://git.kernel.org/stable/c/c4593f1654f7dea3bcf9bb1851ded86311d4f370
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31731.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
