# [H] ALSA: timer: Fix UAF at snd_timer_user_params()

## Summary
Severity: High
Advisory: CVE-2026-53192
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53192
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: Fix UAF at snd_timer_user_params()

At releasing a timer object, e.g. when a userspace timer
(CONFIG_SND_UTIMER) gets closed and snd_timer_free() is called, it
tries to detach the timer instances and release the resources.
However, it's still possible that other in-flight tasks are holding
the timer instance where the to-be-deleted timer object is associated,
and this may lead to racy accesses.

Fortunately, most of ioctls dealing with the timer instance list
already have the protection with register_mutex, and this also avoids
such races.  But, SNDRV_TIMER_IOCTL_PARAMS isn't protected, hence the
concurrent ioctl may lead to use-after-free.

This patch just adds the guard with register_mutex to protect
snd_timer_user_params() for covering the code path as a quick
workaround.  It's no hot-path but rather a rarely issued ioctl, so the
performance penalty doesn't matter.

## References
- https://git.kernel.org/stable/c/053a401b592be424fea9d57c789f66cd5d8cec11
- https://git.kernel.org/stable/c/306427adf9b97e29e5958cb9cf3096c6151fc9ff
- https://git.kernel.org/stable/c/38034d04d4a75bbca01df2b313ced0bcd0fa3242
- https://git.kernel.org/stable/c/3d39da65b5c422c5e5afb7d5651b0698d060a827
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53192.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
