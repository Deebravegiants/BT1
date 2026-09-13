# [H] ALSA: timer: don't re-enter an instance callback that is still running

## Summary
Severity: High
Advisory: CVE-2026-68200
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68200
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: don't re-enter an instance callback that is still running

The userspace-driven timer (utimer) TRIGGER ioctl calls
snd_timer_interrupt() directly with no serialization, so two threads
triggering the same utimer can run snd_timer_interrupt() on one
snd_timer concurrently.

snd_timer_process_callbacks() drops timer->lock around each instance
callback and marks the in-flight callback with the single
SNDRV_TIMER_IFLG_CALLBACK bit; snd_timer_close_locked() waits on that
bit to drain an in-flight callback before freeing the instance. The bit
cannot represent two concurrent callbacks: when a second interrupt
re-queues an instance whose callback is still running, both run at once,
the first to finish clears the bit, and the close-path drain then frees
the instance (and its callback_data) while the other callback is still
live - a use-after-free reachable by any user able to open
/dev/snd/timer, both via a user timer instance and via a sequencer queue
timer bound to the utimer.

snd_timer_interrupt() sets IFLG_CALLBACK before dropping timer->lock, so
a concurrent interrupt already observes it under the lock. Skip
re-queuing an instance (and its slaves) to the ack/sack list while its
callback is in flight; the accumulated pticks are delivered on the next
tick, so no event is lost.

## References
- https://git.kernel.org/stable/c/1395327a96614885552bae5fbb650e6dd182d49b
- https://git.kernel.org/stable/c/70d28bfcd6224eed75986b3b987b997e59643fa4
- https://git.kernel.org/stable/c/996c24377eea4d4506b7c3ccbbf1e490440b5e0b
- https://git.kernel.org/stable/c/c1078130a4cd7e738f4b73afe99b3e68cbfbf884
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
