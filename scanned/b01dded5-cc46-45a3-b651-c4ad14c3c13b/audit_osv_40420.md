# [H] timers/migration: Fix livelock in tmigr_handle_remote_up()

## Summary
Severity: High
Advisory: CVE-2026-53180
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53180
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

timers/migration: Fix livelock in tmigr_handle_remote_up()

tmigr_handle_remote_cpu() skips timer_expire_remote() when cpu ==
smp_processor_id(), assuming the local softirq path already handled this
CPU's timers.

This assumption is wrong because jiffies can advance after the handling of
the CPU's global timers in run_timer_base(BASE_GLOBAL) and before
tmigr_handle_remote() evaluates the expiry times.

As a consequence a timer which expires after the CPU local timer wheel
advanced and becomes expired in the remote handling is ignored and the
callback is never invoked and removed from the timer wheel.

What's worse is that fetch_next_timer_interrupt_remote() keeps reporting it
as expired, and the event is re-queued with expires == now on each
iteration.  The goto-again loop spins indefinitely.

Fix this by calling timer_expire_remote() unconditionally. That's minimal
overhead for the common case as __run_timer_base() returns immediately if
there is nothing to expire in the local wheel.

[ tglx: Amend change log and add a comment ]

## References
- https://git.kernel.org/stable/c/07b3b83587fb3012619f4439389b64a955fc7836
- https://git.kernel.org/stable/c/1d6c2062b77be09ec15d6bf637b2e2221c4482fc
- https://git.kernel.org/stable/c/d338e61ea94052a786aac9f58e9f0d8520afa0fd
- https://git.kernel.org/stable/c/d486b4934a8e504376b85cdb3766f306d57aff5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53180.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
