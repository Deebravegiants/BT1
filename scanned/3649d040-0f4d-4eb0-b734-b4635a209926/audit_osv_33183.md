# [H] ptp: ocp: fix use-after-free bugs causing by ptp_ocp_watchdog

## Summary
Severity: High
Advisory: CVE-2025-39859
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39859
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: ocp: fix use-after-free bugs causing by ptp_ocp_watchdog

The ptp_ocp_detach() only shuts down the watchdog timer if it is
pending. However, if the timer handler is already running, the
timer_delete_sync() is not called. This leads to race conditions
where the devlink that contains the ptp_ocp is deallocated while
the timer handler is still accessing it, resulting in use-after-free
bugs. The following details one of the race scenarios.

(thread 1)                           | (thread 2)
ptp_ocp_remove()                     |
  ptp_ocp_detach()                   | ptp_ocp_watchdog()
    if (timer_pending(&bp->watchdog))|   bp = timer_container_of()
      timer_delete_sync()            |
                                     |
  devlink_free(devlink) //free       |
                                     |   bp-> //use

Resolve this by unconditionally calling timer_delete_sync() to ensure
the timer is reliably deactivated, preventing any access after free.

## References
- https://git.kernel.org/stable/c/8bf935cf789872350b04c1a6468b0a509f67afb2
- https://git.kernel.org/stable/c/f10d3c7267ac7387a5129d5506c3c5f2460cfd9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39859.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
