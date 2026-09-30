# [H] ALSA: timer: Forcibly close timer instances at closing

## Summary
Severity: High
Advisory: CVE-2026-53193
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53193
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: Forcibly close timer instances at closing

When snd_timer object is freed via snd_timer_free() and still pending
snd_timer_instance objects are assigned to the timer object, it tries
to unlink all instances and just set NULL to each ti->timer, then
releases the resources immediately.  The problem is, however, when
there are slave timer instances that are associated with a master
instance linked to this timer: namely, those slave instances still
point to the freed timer object although the master instance is
unlinked, which may lead to user-after-free.  The bug can be easily
triggered particularly when a new userspace-driven timers
(CONFIG_SND_UTIMER) is involved, since it can create and delete the
timer object via a simple file open/close, while the other
applications may keep accessing to that timer.

This patch is an attempt to paper over the problem above: now instead
of just unlinking, call snd_timer_close[_locked]() forcibly for each
pending timer instance, so that all assigned slave timer instances are
properly detached, too.  Since snd_timer_close() might be called later
by the driver that created that instance, the check of
SNDRV_TIMER_IFLG_DEAD is added at the beginning, too.

## References
- https://git.kernel.org/stable/c/586b219a22b1032b28b8bd356b963276c5e5bf53
- https://git.kernel.org/stable/c/60e73ab87b84bbd6bd7ddd1d16019a3a3705ab8f
- https://git.kernel.org/stable/c/da3039e91d1f835874ed6e9a33ea19ee80c2cb92
- https://git.kernel.org/stable/c/f46093dd22969037beb1fce2e043f3236be41c92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53193.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53193
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
