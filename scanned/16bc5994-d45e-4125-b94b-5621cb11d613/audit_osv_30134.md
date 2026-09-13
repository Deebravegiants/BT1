# [M] USB: gadget: dummy-hcd: Fix "task hung" problem

## Summary
Severity: Medium
Advisory: CVE-2024-50100
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50100
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: gadget: dummy-hcd: Fix "task hung" problem

The syzbot fuzzer has been encountering "task hung" problems ever
since the dummy-hcd driver was changed to use hrtimers instead of
regular timers.  It turns out that the problems are caused by a subtle
difference between the timer_pending() and hrtimer_active() APIs.

The changeover blindly replaced the first by the second.  However,
timer_pending() returns True when the timer is queued but not when its
callback is running, whereas hrtimer_active() returns True when the
hrtimer is queued _or_ its callback is running.  This difference
occasionally caused dummy_urb_enqueue() to think that the callback
routine had not yet started when in fact it was almost finished.  As a
result the hrtimer was not restarted, which made it impossible for the
driver to dequeue later the URB that was just enqueued.  This caused
usb_kill_urb() to hang, and things got worse from there.

Since hrtimers have no API for telling when they are queued and the
callback isn't running, the driver must keep track of this for itself.
That's what this patch does, adding a new "timer_pending" flag and
setting or clearing it at the appropriate times.

## References
- https://git.kernel.org/stable/c/5189df7b8088268012882c220d6aca4e64981348
- https://git.kernel.org/stable/c/7d85884576a3be3616c260fc1fa862a59579d1ab
- https://git.kernel.org/stable/c/cf7ee2291da551fc4b109fda1f6a332cb8212065
- https://git.kernel.org/stable/c/f828205ee3e4ddc712a13fba6c9902d51e91ddaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50100.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
