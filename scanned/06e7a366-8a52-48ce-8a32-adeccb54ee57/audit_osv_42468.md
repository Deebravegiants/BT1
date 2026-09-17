# [H] ALSA: seq: close a re-opened queue timer in the destructor

## Summary
Severity: High
Advisory: CVE-2026-68202
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68202
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: seq: close a re-opened queue timer in the destructor

queue_delete() closes the queue timer, then frees it. snd_seq_timer_close()
clears q->timer->timeri. snd_use_lock_sync() then drains borrowers, and
snd_seq_timer_delete() frees q->timer.

A borrower can re-open the timer inside that window. A SET_QUEUE_CLIENT
that took a queueptr() use_lock reference before the queue was unlinked
runs snd_seq_timer_open() after the close. Open refuses re-open only while
timeri is set, and the close just cleared it, so it re-opens timeri.

snd_seq_timer_delete() does not close that instance. Its snd_seq_timer_stop()
is a no-op, because running was cleared first. So it frees q->timer with the
instance still live. The queue is freed next.

The instance stays on the global timer with callback_data pointing at the
freed queue. A non-owner START on the unlocked queue arms it. The next tick
derefs the freed queue in snd_seq_timer_interrupt().

Reachable by an unprivileged user with access to /dev/snd/seq. No CAP and
no queue ownership required.

Close any lingering instance in the destructor. There, ->timeri can no
longer change: the queue is unlinked and all use_lock borrowers have
drained, so no snd_seq_queue_use() can re-open it. Close it before clearing
q->timer. snd_timer_close() waits for any in-flight snd_seq_timer_interrupt()
to finish, and that callback still reads q->timer (via snd_seq_check_queue()),
so q->timer must stay valid until it drains.

## References
- https://git.kernel.org/stable/c/24f0cabf173539f048946c8fc221131dc221f277
- https://git.kernel.org/stable/c/2c4dc0ed50b05cd847a4b34b8cebf0775f19aeb9
- https://git.kernel.org/stable/c/31a6163e301d832060f8236f1ed17cbc1ca198df
- https://git.kernel.org/stable/c/6a10025c7fd09a7d2af37a3ae1da188569fce470
- https://git.kernel.org/stable/c/7478ef94b49bc9789cf1a003deec58b42283dde4
- https://git.kernel.org/stable/c/9d9be6fc30f384f92c4e1b8ed40bd9d4796b7833
- https://git.kernel.org/stable/c/b7feeaca1f53b10df9b4de9eaf611767ca70dc92
- https://git.kernel.org/stable/c/fb40d03ed792a8a8bf77aa0ee15df57b0ff78b07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68202.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
