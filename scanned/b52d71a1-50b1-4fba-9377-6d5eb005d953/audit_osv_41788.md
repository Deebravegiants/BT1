# [H] net: mctp: usb: fix race between urb completion and rx_retry cancellation

## Summary
Severity: High
Advisory: CVE-2026-63874
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63874
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mctp: usb: fix race between urb completion and rx_retry cancellation

It's possible that sequencing between setting ->stopped and cancelling
the rx_retry work (in ndo_stop) could leave us with an urb queued:

    T1: ndo_stop                  T2: rx_retry_work
    ------------                  ----------------
                                  LD: ->stopped => false
    ST: ->stopped <= true
    usb_kill_urb()
                                  mctp_usb_rx_queue()
                                    usb_submit_urb()
    cancel_delayed_work_sync()

That urb completion can then re-schedule rx_retry_work.

Strenghen the sequencing between the stop (preventing another requeue)
and the cancel by updating both atomically under a new rx lock. After
setting ->rx_stopped, and cancelling pending work, we know that the
requeue cannot occur, so all that's left is killing any pending urb.

## References
- https://git.kernel.org/stable/c/54665dce982689e2fd99b32e9a0dcc204fda8a51
- https://git.kernel.org/stable/c/9c46f3ee1837f6881cb99a52ffecb2760f11dc73
- https://git.kernel.org/stable/c/d90feaa3f74bea8dafb6494631a194c70e547d94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63874.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
