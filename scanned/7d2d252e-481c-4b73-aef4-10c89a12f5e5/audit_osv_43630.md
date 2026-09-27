# [H] ALSA: timer: Clear SNDRV_TIMER_IFLG_DEAD once the close completes

## Summary
Severity: High
Advisory: CVE-2026-74503
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74503
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: Clear SNDRV_TIMER_IFLG_DEAD once the close completes

snd_timer_close_locked() marks an instance with SNDRV_TIMER_IFLG_DEAD
and returns early when the flag is already set, but the flag is never
cleared again.  A completed close ends in remove_slave_links(), which
leaves timeri->timer NULL, so a second close is already harmless through
the timer == NULL path; the early return can only be reached by an
instance that was opened again in between.  For such an instance the
close unlinks nothing, so snd_timer_instance_free() frees an object that
is still on timer->open_list_head, still on snd_timer_master_list if it
was opened with a slave key, still owns any adopted slaves, and still
holds its timer and module references.

snd_seq_timer_open() reopens an instance exactly like that: it retries
its fallback open on the same object after a failure that has already
run snd_timer_close_locked() internally.  An unprivileged user with
access to /dev/snd/timer and /dev/snd/seq can force that failure, since
snd_timer_check_master() returns -EBUSY when a pending slave matches the
new master's (slave_class, slave_id) key and the target timer has
reached max_instances, and SNDRV_TIMER_IOCTL_SELECT with dev_class =
SNDRV_TIMER_CLASS_SLAVE keeps the caller-supplied dev_sclass, so a
sequencer queue's key can be forged.  The freed instance is afterwards
dereferenced by any further snd_timer_open() on that timer, by
snd_timer_check_slave(), and by /proc/asound/timers, which faults on the
stale ti->owner pointer.

The flag only has to be visible while the close is in progress, which is
all its other users need.  Clear it in remove_slave_links(), under the
same timer->lock that sets it, once the instance is off every list.

## References
- https://git.kernel.org/stable/c/0c561fab50991df10b1e4daca25886c34a2a9c07
- https://git.kernel.org/stable/c/a26a2e52736f9e39843ca66a2e1ce6bf1adbcd1e
- https://git.kernel.org/stable/c/bb016091010ec401a06e6bdace0cd944ee03d371
- https://git.kernel.org/stable/c/c2744d5f3aea474513fd2298daecb94a952ce441
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74503.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74503
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
